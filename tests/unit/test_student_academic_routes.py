"""Consultas academicas do proprio usuario e armazenamento administrativo."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.core.security import get_current_active_user
from backend.app.core.seed import seed_database
from backend.app.main import app
from backend.app.models.academic import Attendance, Enrollment
from backend.app.models.user import User


@pytest.fixture
def seeded_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)
    db = test_session()
    seed_database(db)

    users = {user.username: user for user in db.query(User).all()}
    actor = [users["aluno"]]

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

    yield {"client": client, "db": db, "users": users, "actor": actor}

    client.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)
    db.close()
    engine.dispose()


def test_student_profile_returns_course_class_and_enrollments(seeded_api):
    response = seeded_api["client"].get("/api/v1/academic/my-profile")

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "student"
    assert body["user"]["full_name"] == "Lucas Santos"
    assert body["student"]["ra"] == "RA123456"
    assert body["student"]["course"]["code"] == "ES01"
    assert body["student"]["class"]["code"] == "ES-IA-20261-A"
    assert body["current_period"]["name"] == "2026.1"
    assert len(body["student"]["enrollments"]) == 2


def test_teacher_profile_lists_assignments(seeded_api):
    seeded_api["actor"][0] = seeded_api["users"]["professor"]

    response = seeded_api["client"].get("/api/v1/academic/my-profile")

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "teacher"
    assert body["teacher"]["employee_id"] == "PROF001"
    assignments = body["teacher"]["assignments"]
    assert len(assignments) == 1
    assert assignments[0]["subject_name"] == "Inteligência Artificial Aplicada"
    assert assignments[0]["class_name"].startswith("Turma A")


def test_student_schedule_returns_classes_with_teacher(seeded_api):
    response = seeded_api["client"].get("/api/v1/academic/schedule/my")

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert {item["subject_name"] for item in items} == {
        "Inteligência Artificial Aplicada",
        "Engenharia de Software",
    }
    assert all(item["teacher_name"] for item in items)
    assert all(item["schedule"] for item in items)


def test_student_attendance_summary_computes_percentage(seeded_api):
    db = seeded_api["db"]
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == seeded_api["users"]["aluno"].student_profile.id)
        .first()
    )
    teacher_user = seeded_api["users"]["professor"]
    db.add_all(
        [
            Attendance(
                enrollment_id=enrollment.id,
                class_date=date(2026, 3, 2),
                is_present=True,
                recorded_by=teacher_user.id,
            ),
            Attendance(
                enrollment_id=enrollment.id,
                class_date=date(2026, 3, 4),
                is_present=True,
                recorded_by=teacher_user.id,
            ),
            Attendance(
                enrollment_id=enrollment.id,
                class_date=date(2026, 3, 9),
                is_present=False,
                justified=True,
                justification="Atestado médico",
                recorded_by=teacher_user.id,
            ),
        ]
    )
    db.commit()

    response = seeded_api["client"].get("/api/v1/academic/attendance/my")

    assert response.status_code == 200
    summaries = response.json()
    summary = next(item for item in summaries if item["enrollment_id"] == str(enrollment.id))
    assert summary["total_classes"] == 3
    assert summary["present_count"] == 2
    assert summary["absent_count"] == 1
    assert summary["justified_count"] == 1
    assert summary["percentage"] == "66.67"
    assert summary["records"][-1]["justification"] == "Atestado médico"


def test_attendance_requires_student_profile(seeded_api):
    seeded_api["actor"][0] = seeded_api["users"]["professor"]

    response = seeded_api["client"].get("/api/v1/academic/attendance/my")

    assert response.status_code == 404
    assert "aluno" in response.json()["detail"].lower()


def test_storage_usage_lists_monitored_folders(seeded_api):
    seeded_api["actor"][0] = seeded_api["users"]["admin"]

    response = seeded_api["client"].get("/api/v1/admin/settings/storage")

    assert response.status_code == 200
    body = response.json()
    keys = {folder["key"] for folder in body["folders"]}
    assert {"exams", "pdfs", "processed", "temp", "materials", "backups"} <= keys
    assert body["database_bytes"] >= 0
    assert body["total_bytes"] >= body["database_bytes"]
    assert body["generated_at"]


def test_storage_usage_is_admin_only(seeded_api):
    response = seeded_api["client"].get("/api/v1/admin/settings/storage")

    assert response.status_code == 403
