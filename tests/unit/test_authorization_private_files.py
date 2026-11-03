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
from backend.app.models.academic import AcademicPeriod, Class, Course, Subject
from backend.app.models.exam import (
    AnswerKey,
    Exam,
    ExamCopy,
    ExamQuestion,
    ExamStatus,
    ExamSubmission,
    ExamVersion,
    QuestionType,
    SubmissionStatus,
)
from backend.app.models.user import Student, User, UserRole


@pytest.fixture
def authorization_api():
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
        email="DADO_DE_TESTE_EDUGRADE.admin@example.test",
        username="DADO_DE_TESTE_EDUGRADE_admin",
        hashed_password="not-a-real-password",
        full_name="DADO_DE_TESTE_EDUGRADE Admin",
        role=UserRole.ADMIN,
    )
    teacher = User(
        id=uuid4(),
        email="DADO_DE_TESTE_EDUGRADE.teacher@example.test",
        username="DADO_DE_TESTE_EDUGRADE_teacher",
        hashed_password="not-a-real-password",
        full_name="DADO_DE_TESTE_EDUGRADE Teacher",
        role=UserRole.TEACHER,
    )
    student_user = User(
        id=uuid4(),
        email="DADO_DE_TESTE_EDUGRADE.student@example.test",
        username="DADO_DE_TESTE_EDUGRADE_student",
        hashed_password="not-a-real-password",
        full_name="DADO_DE_TESTE_EDUGRADE Student",
        role=UserRole.STUDENT,
    )
    other_student_user = User(
        id=uuid4(),
        email="DADO_DE_TESTE_EDUGRADE.other@example.test",
        username="DADO_DE_TESTE_EDUGRADE_other",
        hashed_password="not-a-real-password",
        full_name="DADO_DE_TESTE_EDUGRADE Other Student",
        role=UserRole.STUDENT,
    )
    student = Student(id=uuid4(), user=student_user, ra="DADO_DE_TESTE_EDUGRADE-1")
    other_student = Student(id=uuid4(), user=other_student_user, ra="DADO_DE_TESTE_EDUGRADE-2")

    course = Course(code="DADO_TESTE", name="DADO_DE_TESTE_EDUGRADE Course")
    period = AcademicPeriod(
        code="DADO_TESTE",
        name="DADO_DE_TESTE_EDUGRADE Period",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
    subject = Subject(code="DADO_TESTE", name="DADO_DE_TESTE_EDUGRADE Subject", course=course)
    class_ = Class(
        code="DADO_TESTE",
        name="DADO_DE_TESTE_EDUGRADE Class",
        course=course,
        subject=subject,
        academic_period=period,
        semester=1,
        year=2026,
    )
    exam = Exam(
        title="DADO_DE_TESTE_EDUGRADE Exam",
        class_=class_,
        subject=subject,
        academic_period=period,
        created_by=admin.id,
        total_score=Decimal("10.00"),
    )
    version = ExamVersion(
        exam=exam,
        version_number=1,
        title=exam.title,
        total_score=Decimal("10.00"),
        questions_snapshot=[],
        answer_key_snapshot={},
        rubrics_snapshot={},
        published_by=admin.id,
    )
    question = ExamQuestion(
        exam=exam,
        question_order=1,
        type=QuestionType.ESSAY,
        statement="DADO_DE_TESTE_EDUGRADE question",
        score=Decimal("10.00"),
    )
    question.answer_key = AnswerKey(
        correct_answer="DADO_DE_TESTE_EDUGRADE answer",
        expected_answer="DADO_DE_TESTE_EDUGRADE expected",
    )
    own_copy = ExamCopy(
        version=version,
        copy_identifier="DADO_DE_TESTE_EDUGRADE-OWN",
        qr_code_data="DADO_DE_TESTE_EDUGRADE-OWN",
        student=student,
    )
    other_copy = ExamCopy(
        version=version,
        copy_identifier="DADO_DE_TESTE_EDUGRADE-OTHER",
        qr_code_data="DADO_DE_TESTE_EDUGRADE-OTHER",
        student=other_student,
    )
    own_submission = ExamSubmission(
        copy=own_copy,
        version=version,
        student=student,
        status=SubmissionStatus.AWAITING_CORRECTION,
        original_files=["private/own.pdf"],
    )
    other_submission = ExamSubmission(
        copy=other_copy,
        version=version,
        student=other_student,
        status=SubmissionStatus.UPLOADED,
        original_files=["private/other.pdf"],
    )
    db.add_all(
        [
            admin,
            teacher,
            student_user,
            other_student_user,
            student,
            other_student,
            course,
            period,
            subject,
            class_,
            exam,
            version,
            question,
            own_copy,
            other_copy,
            own_submission,
            other_submission,
        ]
    )
    db.commit()
    actor = [student_user]

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
        "admin": admin,
        "teacher": teacher,
        "student": student,
        "other_student": other_student,
        "question": question,
        "exam": exam,
        "version": version,
        "db": db,
        "own_submission": own_submission,
        "other_submission": other_submission,
    }
    yield data
    client.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)
    db.close()
    engine.dispose()


def test_teachers_can_list_active_published_versions_and_create_unique_upload_copies(authorization_api):
    client = authorization_api["client"]
    actor = authorization_api["actor"]
    exam = authorization_api["exam"]
    version = authorization_api["version"]
    exam.status = ExamStatus.PUBLISHED
    authorization_api["db"].commit()

    assert client.get("/api/v1/exams/versions/active").status_code == 403

    actor[0] = authorization_api["teacher"]
    listed = client.get("/api/v1/exams/versions/active")

    assert listed.status_code == 200
    assert listed.json() == [
        {
            "version_id": str(version.id),
            "exam_id": str(exam.id),
            "title": version.title,
            "version_number": version.version_number,
            "class_id": str(exam.class_id),
            "class_name": exam.class_.name,
            "subject_name": exam.subject.name,
        }
    ]

    first = client.post(
        f"/api/v1/exams/versions/{version.id}/copies",
        params={"count": 1, "student_ids": str(authorization_api["student"].id)},
    )
    second = client.post(
        f"/api/v1/exams/versions/{version.id}/copies",
        params={"count": 1, "student_ids": str(authorization_api["student"].id)},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()[0]["copy_identifier"].endswith("-0003")
    assert second.json()[0]["copy_identifier"].endswith("-0004")


def test_students_only_list_and_read_their_own_limited_submissions(authorization_api):
    client = authorization_api["client"]
    own_id = authorization_api["own_submission"].id
    other_id = authorization_api["other_submission"].id

    listed = client.get(
        "/api/v1/exams/submissions",
        params={"student_id": str(authorization_api["other_student"].id)},
    )

    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 1
    assert [item["id"] for item in body["items"]] == [str(own_id)]
    assert set(body["items"][0]) == {"id", "status", "submitted_at", "processed_at"}
    assert "private/own.pdf" not in listed.text
    assert "DADO_DE_TESTE_EDUGRADE-OTHER" not in listed.text

    own = client.get(f"/api/v1/exams/submissions/{own_id}")
    other = client.get(f"/api/v1/exams/submissions/{other_id}")

    assert own.status_code == 200
    assert own.json()["id"] == str(own_id)
    assert set(own.json()) == {"id", "status", "submitted_at", "processed_at"}
    assert other.status_code == 404


def test_students_do_not_receive_answer_keys_but_staff_can(authorization_api):
    client = authorization_api["client"]
    question_id = authorization_api["question"].id

    student_list = client.get(f"/api/v1/exams/{authorization_api['exam'].id}/questions")
    student_question = client.get(f"/api/v1/exams/questions/{question_id}")

    assert student_list.status_code == 200
    assert len(student_list.json()) == 1
    assert "answer_key" not in student_list.json()[0]
    assert student_question.status_code == 200
    assert "answer_key" not in student_question.json()
    assert "DADO_DE_TESTE_EDUGRADE answer" not in student_question.text

    for role in ("teacher", "admin"):
        authorization_api["actor"][0] = authorization_api[role]
        staff_question = client.get(f"/api/v1/exams/questions/{question_id}")
        assert staff_question.status_code == 200
        assert staff_question.json()["answer_key"]["correct_answer"] == "DADO_DE_TESTE_EDUGRADE answer"


def test_private_storage_is_not_mounted_and_students_cannot_download_exam_pdfs(authorization_api):
    client = authorization_api["client"]

    assert client.get("/storage/private-marker.txt").status_code == 404
    assert client.post(f"/api/v1/exams/copies/{uuid4()}/pdf-student").status_code == 403
    assert client.post(f"/api/v1/exams/versions/{uuid4()}/pdf-teacher").status_code == 403
