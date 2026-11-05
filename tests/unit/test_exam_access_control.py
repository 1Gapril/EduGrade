"""Testes de escopo e autorização das rotas de provas."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.core.security import get_current_active_user
from backend.app.main import app
from backend.app.models.academic import (
    AcademicPeriod,
    Class,
    Course,
    Enrollment,
    EnrollmentStatus,
    Subject,
    TeacherSubject,
)
from backend.app.models.exam import Exam, ExamQuestion, ExamStatus, QuestionType
from backend.app.models.user import Student, Teacher, User, UserRole


def _make_user(role: UserRole, suffix: str) -> User:
    return User(
        id=uuid4(),
        email=f"{suffix}@example.test",
        username=suffix,
        hashed_password="not-a-real-password",
        full_name=suffix,
        role=role,
    )


@pytest.fixture
def exams_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)
    db = test_session()

    admin = _make_user(UserRole.ADMIN, "admin")
    teacher_user = _make_user(UserRole.TEACHER, "teacher_a")
    other_teacher_user = _make_user(UserRole.TEACHER, "teacher_b")
    student_user = _make_user(UserRole.STUDENT, "student_a")
    other_student_user = _make_user(UserRole.STUDENT, "student_b")

    teacher = Teacher(id=uuid4(), user=teacher_user, employee_id="EMP-A")
    other_teacher = Teacher(id=uuid4(), user=other_teacher_user, employee_id="EMP-B")
    student = Student(id=uuid4(), user=student_user, ra="RA-A")
    other_student = Student(id=uuid4(), user=other_student_user, ra="RA-B")

    course = Course(code="COD_A", name="Course A")
    period = AcademicPeriod(
        code="PER_A",
        name="Period A",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
    subject = Subject(code="SUB_A", name="Subject A", course=course)
    class_a = Class(
        code="CLS_A",
        name="Class A",
        course=course,
        subject=subject,
        academic_period=period,
        semester=1,
        year=2026,
        teacher=teacher,
    )
    class_b = Class(
        code="CLS_B",
        name="Class B",
        course=course,
        subject=subject,
        academic_period=period,
        semester=1,
        year=2026,
        teacher=other_teacher,
    )
    teacher_subject = TeacherSubject(
        teacher=teacher,
        subject=subject,
        academic_period=period,
    )

    enrollment = Enrollment(
        student=student,
        class_=class_a,
        academic_period=period,
        status=EnrollmentStatus.ACTIVE,
    )

    draft_exam = Exam(
        title="Prova rascunho",
        class_=class_a,
        subject=subject,
        academic_period=period,
        created_by=teacher_user.id,
        total_score=Decimal("10.00"),
        status=ExamStatus.DRAFT,
    )
    published_exam = Exam(
        title="Prova publicada",
        class_=class_a,
        subject=subject,
        academic_period=period,
        created_by=teacher_user.id,
        total_score=Decimal("10.00"),
        status=ExamStatus.PUBLISHED,
    )
    other_exam = Exam(
        title="Prova de outro professor",
        class_=class_b,
        subject=subject,
        academic_period=period,
        created_by=other_teacher_user.id,
        total_score=Decimal("10.00"),
        status=ExamStatus.DRAFT,
    )
    question = ExamQuestion(
        exam=draft_exam,
        question_order=1,
        type=QuestionType.ESSAY,
        statement="Questão",
        score=Decimal("10.00"),
    )

    db.add_all(
        [
            admin,
            teacher_user,
            other_teacher_user,
            student_user,
            other_student_user,
            teacher,
            other_teacher,
            student,
            other_student,
            course,
            period,
            subject,
            class_a,
            class_b,
            teacher_subject,
            enrollment,
            draft_exam,
            published_exam,
            other_exam,
            question,
        ]
    )
    db.commit()

    actor = [teacher_user]

    def override_db():
        session = test_session()
        try:
            yield session
        finally:
            session.close()

    def override_user():
        return actor[0]

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_active_user] = override_user
    client = TestClient(app, raise_server_exceptions=False)

    data = {
        "client": client,
        "actor": actor,
        "db": db,
        "admin": admin,
        "teacher_user": teacher_user,
        "other_teacher_user": other_teacher_user,
        "student_user": student_user,
        "other_student_user": other_student_user,
        "class_a": class_a,
        "class_b": class_b,
        "draft_exam": draft_exam,
        "published_exam": published_exam,
        "other_exam": other_exam,
        "question": question,
        "student": student,
    }
    yield data

    client.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)
    db.close()
    engine.dispose()


def test_teacher_exam_listing_uses_consistent_pagination(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]

    by_class = client.get(
        "/api/v1/exams",
        params={"class_id": str(exams_api["class_a"].id)},
    )
    assert by_class.status_code == 200
    assert by_class.json()["total"] == 2

    by_status = client.get("/api/v1/exams", params={"status": "published"})
    assert by_status.status_code == 200
    assert by_status.json()["total"] == 1

    all_exams = client.get("/api/v1/exams")
    assert all_exams.status_code == 200
    body = all_exams.json()
    assert body["total"] == 2
    assert all(item["class_id"] == str(exams_api["class_a"].id) for item in body["items"])


def test_teacher_cannot_filter_exams_of_other_teachers(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]

    response = client.get(
        "/api/v1/exams",
        params={"class_id": str(exams_api["class_b"].id)},
    )

    assert response.status_code == 403


def test_invalid_exam_status_returns_422(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]

    response = client.get("/api/v1/exams", params={"status": "inexistente"})

    assert response.status_code == 422


def test_teacher_cannot_update_or_cancel_exam_of_another_teacher(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]
    other_exam_id = exams_api["other_exam"].id

    update = client.patch(
        f"/api/v1/exams/{other_exam_id}",
        json={"title": "Prova roubada"},
    )
    cancel = client.delete(f"/api/v1/exams/{other_exam_id}")

    assert update.status_code == 403
    assert cancel.status_code == 403


def test_teacher_can_update_own_exam(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]
    draft_exam = exams_api["draft_exam"]

    response = client.patch(
        f"/api/v1/exams/{draft_exam.id}",
        json={"title": "Prova atualizada"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Prova atualizada"


def test_teacher_cannot_move_own_exam_to_another_teachers_class(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]
    draft_exam = exams_api["draft_exam"]

    response = client.patch(
        f"/api/v1/exams/{draft_exam.id}/complete",
        json={
            "title": "Prova completa",
            "class_id": str(exams_api["class_b"].id),
            "subject_id": str(exams_api["draft_exam"].subject_id),
            "academic_period_id": str(exams_api["draft_exam"].academic_period_id),
            "total_score": "10.00",
            "duration_minutes": 120,
            "questions": [
                {
                    "type": "essay",
                    "statement": "Questão",
                    "score": "10.00",
                    "expected_answer": "Resposta",
                }
            ],
        },
    )

    assert response.status_code == 403


def test_teacher_can_update_own_exam_with_questions(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]
    draft_exam = exams_api["draft_exam"]
    question = exams_api["question"]

    response = client.patch(
        f"/api/v1/exams/{draft_exam.id}/complete",
        json={
            "title": "Prova completa",
            "class_id": str(exams_api["class_a"].id),
            "subject_id": str(draft_exam.subject_id),
            "academic_period_id": str(draft_exam.academic_period_id),
            "total_score": "10.00",
            "duration_minutes": 120,
            "questions": [
                {
                    "id": str(question.id),
                    "type": "essay",
                    "statement": "Questão atualizada",
                    "score": "10.00",
                    "expected_answer": "Resposta",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Prova completa"


def test_teacher_cancels_own_exam(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["teacher_user"]
    published_exam = exams_api["published_exam"]

    response = client.delete(f"/api/v1/exams/{published_exam.id}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_students_only_list_visible_exams_of_their_classes(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["student_user"]

    response = client.get("/api/v1/exams")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert [item["id"] for item in body["items"]] == [str(exams_api["published_exam"].id)]


def test_students_cannot_read_draft_exams(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["student_user"]

    response = client.get(f"/api/v1/exams/{exams_api['draft_exam'].id}")

    assert response.status_code == 404


def test_admin_still_lists_all_exams(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["admin"]

    response = client.get("/api/v1/exams")

    assert response.status_code == 200
    assert response.json()["total"] == 3


def test_admin_listing_reports_full_total_when_paginated(exams_api):
    client = exams_api["client"]
    exams_api["actor"][0] = exams_api["admin"]

    response = client.get("/api/v1/exams", params={"page_size": 1, "page": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 1
    assert body["has_next"] is True
    assert body["has_prev"] is True
