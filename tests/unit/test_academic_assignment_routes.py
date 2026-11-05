from datetime import date
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.routes.academic import require_class_permission
from backend.app.core.database import Base, get_db
from backend.app.core.security import get_current_active_user
from backend.app.main import app
from backend.app.models.academic import (
    AcademicAssignment,
    AcademicPeriod,
    Class,
    Course,
    Enrollment,
    EnrollmentStatus,
    Subject,
)
from backend.app.models.audit import AuditLog
from backend.app.models.user import Student, Teacher, User, UserRole


@pytest.fixture
def assignment_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)
    db = test_session()

    admin = User(
        id=uuid4(),
        email="admin-assignment@example.test",
        username="admin-assignment",
        full_name="Admin",
        hashed_password="not-a-real-password",
        role=UserRole.ADMIN,
    )
    teacher_user = User(
        id=uuid4(),
        email="teacher-assignment@example.test",
        username="teacher-assignment",
        full_name="Teacher",
        hashed_password="not-a-real-password",
        role=UserRole.TEACHER,
    )
    teacher = Teacher(user=teacher_user, employee_id="EMP-ASSIGNMENT")
    course = Course(code="COURSE-A", name="Course A")
    period = AcademicPeriod(
        code="PERIOD-A",
        name="Period A",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
    subject = Subject(code="SUBJECT-A", name="Subject A", course=course)
    class_record = Class(
        code="CLASS-A",
        name="Class A",
        course=course,
        subject=subject,
        academic_period=period,
        semester=1,
        year=2026,
    )
    db.add_all([admin, teacher_user, teacher, course, period, subject, class_record])
    db.commit()

    actor = [admin]

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = lambda: actor[0]
    with TestClient(app) as client:
        yield {
            "client": client,
            "actor": actor,
            "admin": admin,
            "teacher_user": teacher_user,
            "teacher": teacher,
            "class": class_record,
            "subject": subject,
            "period": period,
            "db": db,
        }
    app.dependency_overrides.clear()
    db.close()
    engine.dispose()


def _assignment_payload(context, permissions):
    return {
        "teacher_id": str(context["teacher"].id),
        "subject_id": str(context["subject"].id),
        "class_id": str(context["class"].id),
        "academic_period_id": str(context["period"].id),
        "permissions": permissions,
    }


def test_admin_creates_and_revokes_contextual_permissions(assignment_api):
    client = assignment_api["client"]
    response = client.post(
        "/api/v1/academic/assignments",
        json=_assignment_payload(assignment_api, {"publish_grades": True}),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["permissions"]["publish_grades"] is True
    assert body["permissions"]["edit_grades"] is False

    assignment_api["actor"][0] = assignment_api["teacher_user"]
    authorized_class = require_class_permission(
        assignment_api["db"],
        assignment_api["teacher_user"],
        assignment_api["class"].id,
        "publish_grades",
    )
    assert authorized_class.id == assignment_api["class"].id
    with pytest.raises(HTTPException) as error:
        require_class_permission(
            assignment_api["db"],
            assignment_api["teacher_user"],
            assignment_api["class"].id,
            "edit_grades",
        )
    assert getattr(error.value, "status_code", None) == 403

    assignment_api["actor"][0] = assignment_api["admin"]
    revoked = client.patch(
        f"/api/v1/academic/assignments/{body['id']}",
        json={"permissions": {"publish_grades": False}},
    )
    assert revoked.status_code == 200
    assert revoked.json()["permissions"]["publish_grades"] is False
    assert assignment_api["db"].query(AuditLog).filter(
        AuditLog.entity_type == "AcademicAssignment"
    ).count() == 2


def test_admin_cannot_create_duplicate_active_context(assignment_api):
    client = assignment_api["client"]
    payload = _assignment_payload(assignment_api, {})
    assert client.post("/api/v1/academic/assignments", json=payload).status_code == 201
    duplicate = client.post("/api/v1/academic/assignments", json=payload)
    assert duplicate.status_code == 409


def test_enrollment_period_must_match_class(assignment_api):
    response = assignment_api["client"].post(
        "/api/v1/academic/enrollments",
        json={
            "student_id": str(uuid4()),
            "class_id": str(assignment_api["class"].id),
            "academic_period_id": str(uuid4()),
        },
    )

    assert response.status_code == 422
    assert "período" in response.json()["detail"]


def test_class_subject_must_belong_to_selected_course(assignment_api):
    response = assignment_api["client"].post(
        "/api/v1/academic/classes",
        json={
            "code": "CLASS-MISMATCH",
            "name": "Mismatched class",
            "course_id": str(uuid4()),
            "subject_id": str(assignment_api["subject"].id),
            "academic_period_id": str(assignment_api["period"].id),
            "semester": 1,
            "year": 2026,
        },
    )

    assert response.status_code == 422
    assert "curso" in response.json()["detail"]


def test_teacher_and_student_subject_queries_follow_active_assignments(assignment_api):
    assignment_response = assignment_api["client"].post(
        "/api/v1/academic/assignments",
        json=_assignment_payload(assignment_api, {}),
    )
    assert assignment_response.status_code == 201

    subject = assignment_api["subject"]
    assignment_api["actor"][0] = assignment_api["teacher_user"]
    teacher_subject = assignment_api["client"].get(f"/api/v1/academic/subjects/{subject.id}")
    assert teacher_subject.status_code == 200
    assignment_api["actor"][0] = assignment_api["admin"]
    revoked = assignment_api["client"].patch(
        f"/api/v1/academic/assignments/{assignment_response.json()['id']}",
        json={"is_active": False},
    )
    assert revoked.status_code == 200
    assignment_api["actor"][0] = assignment_api["teacher_user"]
    assert assignment_api["client"].get(
        f"/api/v1/academic/subjects/{subject.id}"
    ).status_code == 403

    student_user = User(
        id=uuid4(),
        email="subject-student@example.org",
        username="subject-student",
        full_name="Subject Student",
        hashed_password="not-a-real-password",
        role=UserRole.STUDENT,
    )
    student = Student(user=student_user, ra="SUBJECT-RA", registration_number="SUBJECT-MAT")
    other_subject = Subject(
        code="SUBJECT-B",
        name="Subject B",
        course_id=assignment_api["class"].course_id,
    )
    enrollment = Enrollment(
        student=student,
        class_=assignment_api["class"],
        academic_period=assignment_api["period"],
        status=EnrollmentStatus.ACTIVE,
    )
    assignment_api["db"].add_all([student_user, student, other_subject, enrollment])
    assignment_api["db"].commit()
    assignment_api["actor"][0] = student_user

    subjects = assignment_api["client"].get("/api/v1/academic/subjects?page=1&page_size=100")
    unrelated_subject = assignment_api["client"].get(
        f"/api/v1/academic/subjects/{other_subject.id}"
    )

    assert subjects.status_code == 200
    assert [item["id"] for item in subjects.json()["items"]] == [str(subject.id)]
    assert unrelated_subject.status_code == 404


def test_admin_updates_teacher_account_and_profile_together(assignment_api):
    teacher = assignment_api["teacher"]
    response = assignment_api["client"].patch(
        f"/api/v1/users/{teacher.user_id}/academic-profile",
        json={
            "user": {"full_name": "Updated Teacher"},
            "teacher": {
                "employee_id": "EMP-UPDATED",
                "department": "Science",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["full_name"] == "Updated Teacher"
    assert response.json()["teacher"]["employee_id"] == "EMP-UPDATED"


def test_admin_updates_student_registration_and_account(assignment_api):
    student_user = User(
        id=uuid4(),
        email="student-profile@example.org",
        username="student-profile",
        full_name="Student",
        hashed_password="not-a-real-password",
        role=UserRole.STUDENT,
    )
    student = Student(user=student_user, ra="RA-PROFILE", registration_number="MAT-OLD")
    assignment_api["db"].add_all([student_user, student])
    assignment_api["db"].commit()

    response = assignment_api["client"].patch(
        f"/api/v1/users/{student_user.id}/academic-profile",
        json={
            "user": {"full_name": "Updated Student"},
            "student": {
                "ra": "RA-PROFILE",
                "registration_number": "MAT-NEW",
                "status": "active",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["full_name"] == "Updated Student"
    assert response.json()["student"]["registration_number"] == "MAT-NEW"


def test_teacher_updates_student_profile_with_contextual_permission(assignment_api):
    context = assignment_api
    student_user = User(
        id=uuid4(),
        email="teacher-edit-student@example.test",
        username="teacher-edit-student",
        full_name="Student Before",
        hashed_password="not-a-real-password",
        role=UserRole.STUDENT,
    )
    student = Student(
        user=student_user,
        ra="RA-BEFORE",
        registration_number="MAT-BEFORE",
    )
    context["db"].add_all([
        student_user,
        student,
        Enrollment(
            student=student,
            class_=context["class"],
            academic_period=context["period"],
            status=EnrollmentStatus.ACTIVE,
        ),
        AcademicAssignment(
            teacher=context["teacher"],
            subject=context["subject"],
            class_=context["class"],
            academic_period=context["period"],
            assigned_by=context["admin"].id,
            permissions={"edit_students": True},
        ),
    ])
    context["db"].commit()
    context["actor"][0] = context["teacher_user"]

    response = context["client"].patch(
        f"/api/v1/users/{student_user.id}/academic-profile",
        json={
            "user": {"full_name": "Student After"},
            "student": {"ra": "RA-AFTER", "registration_number": "MAT-AFTER"},
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["full_name"] == "Student After"
    assert response.json()["student"]["ra"] == "RA-AFTER"
    assert response.json()["student"]["registration_number"] == "MAT-AFTER"


def test_teacher_cannot_update_student_profile_without_contextual_permission(assignment_api):
    context = assignment_api
    student_user = User(
        id=uuid4(),
        email="teacher-denied-student@example.test",
        username="teacher-denied-student",
        full_name="Student",
        hashed_password="not-a-real-password",
        role=UserRole.STUDENT,
    )
    student = Student(user=student_user, ra="RA-DENIED", registration_number="MAT-DENIED")
    context["db"].add_all([
        student_user,
        student,
        Enrollment(
            student=student,
            class_=context["class"],
            academic_period=context["period"],
            status=EnrollmentStatus.ACTIVE,
        ),
    ])
    context["db"].commit()
    context["actor"][0] = context["teacher_user"]

    response = context["client"].patch(
        f"/api/v1/users/{student_user.id}/academic-profile",
        json={
            "user": {"full_name": "Unauthorized"},
            "student": {"ra": "RA-DENIED", "registration_number": "MAT-DENIED"},
        },
    )

    assert response.status_code == 403, response.text


def test_teacher_creates_student_only_with_contextual_permission(assignment_api):
    context = assignment_api
    context["db"].add(
        AcademicAssignment(
            teacher=context["teacher"],
            subject=context["subject"],
            class_=context["class"],
            academic_period=context["period"],
            assigned_by=context["admin"].id,
            permissions={"create_students": True},
        )
    )
    context["db"].commit()
    context["actor"][0] = context["teacher_user"]

    response = context["client"].post(
        "/api/v1/users/provision",
        json={
            "user": {
                "full_name": "Created Student",
                "username": "created-student",
                "email": "created-student@example.org",
                "password": "Secure-Initial-Password-123",
                "role": "student",
            },
            "student_ra": "RA-CREATED",
            "student_registration_number": "MAT-CREATED",
            "student_class_id": str(context["class"].id),
        },
    )

    assert response.status_code == 201, response.text
    student_id = response.json()["student"]["id"]
    enrollment = context["db"].query(Enrollment).filter_by(student_id=UUID(student_id)).one()
    assert enrollment.class_id == context["class"].id
    assert enrollment.academic_period_id == context["period"].id


def test_teacher_cannot_create_student_without_contextual_permission(assignment_api):
    context = assignment_api
    context["actor"][0] = context["teacher_user"]

    response = context["client"].post(
        "/api/v1/users/provision",
        json={
            "user": {
                "full_name": "Denied Student",
                "username": "denied-student",
                "email": "denied-student@example.org",
                "password": "Secure-Initial-Password-123",
                "role": "student",
            },
            "student_ra": "RA-DENIED-CREATE",
            "student_registration_number": "MAT-DENIED-CREATE",
            "student_class_id": str(context["class"].id),
        },
    )

    assert response.status_code == 403, response.text
