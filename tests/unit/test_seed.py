from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base
from backend.app.core.seed import SEED_ACCOUNTS, seed_database
from backend.app.models.academic import (
    AcademicAssignment,
    AcademicPeriod,
    Class,
    Enrollment,
    Subject,
    TeacherSubject,
)
from backend.app.models.user import Administrator, Student, Teacher, User, UserRole


def _build_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine, Session(engine)


def test_seed_creates_two_accounts_per_role():
    engine, db = _build_session()
    try:
        assert seed_database(db) is True
        assert seed_database(db) is False

        for role in (UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT):
            users = db.execute(select(User).where(User.role == role)).scalars().all()
            assert len(users) == 2, f"esperadas 2 contas para {role}"

        assert {account["role"] for account in SEED_ACCOUNTS} == {
            "admin",
            "teacher",
            "student",
        }
        assert len(SEED_ACCOUNTS) == 6
        assert len({account["username"] for account in SEED_ACCOUNTS}) == 6
    finally:
        db.close()
        engine.dispose()


def test_seed_creates_academic_structure_for_every_account():
    engine, db = _build_session()
    try:
        seed_database(db)

        admins = db.execute(select(Administrator)).scalars().all()
        teachers = db.execute(select(Teacher)).scalars().all()
        students = db.execute(select(Student)).scalars().all()
        classes = db.execute(select(Class)).scalars().all()
        period = db.execute(select(AcademicPeriod)).scalar_one()
        subject = db.execute(select(Subject)).first()
        enrollments = db.execute(select(Enrollment)).scalars().all()

        assert len(admins) == 2
        assert len(teachers) == 2
        assert len(students) == 2
        assert len(classes) == 2
        assert subject is not None
        assert period.is_current is True

        # Cada professor tem disciplina autorizada e atribuição completa na turma.
        for teacher in teachers:
            assignment = db.execute(
                select(TeacherSubject).where(TeacherSubject.teacher_id == teacher.id)
            ).scalar_one()
            assert assignment.academic_period_id == period.id

            academic_assignment = db.execute(
                select(AcademicAssignment).where(
                    AcademicAssignment.teacher_id == teacher.id,
                    AcademicAssignment.is_active.is_(True),
                )
            ).scalar_one()
            assert all(academic_assignment.permissions.values())

        # Cada aluno está matriculado em todas as turmas.
        for student in students:
            student_enrollments = [
                enrollment for enrollment in enrollments if enrollment.student_id == student.id
            ]
            assert len(student_enrollments) == len(classes)
    finally:
        db.close()
        engine.dispose()
