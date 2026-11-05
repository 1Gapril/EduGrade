from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base
from backend.app.core.seed import seed_database
from backend.app.models.academic import AcademicPeriod, Subject, TeacherSubject
from backend.app.models.user import Teacher, User


def test_seed_creates_demo_accounts_and_teacher_subject_assignment():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as db:
            assert seed_database(db) is True
            assert seed_database(db) is False

            teacher = db.execute(
                select(Teacher).join(User).where(User.username == "professor")
            ).scalar_one()
            subject = db.execute(select(Subject)).scalar_one()
            period = db.execute(select(AcademicPeriod)).scalar_one()
            assignment = db.execute(
                select(TeacherSubject).where(TeacherSubject.teacher_id == teacher.id)
            ).scalar_one()

            assert assignment.subject_id == subject.id
            assert assignment.academic_period_id == period.id
    finally:
        engine.dispose()
