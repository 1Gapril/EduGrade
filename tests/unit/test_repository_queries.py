from datetime import date
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.academic import (
    AcademicPeriod,
    AcademicPeriodStatus,
    Class,
    Course,
    Enrollment,
    EnrollmentStatus,
    Subject,
    TeacherSubject,
)
from backend.app.models.user import Student, Teacher, User, UserRole
from backend.app.repositories.academic_repository import (
    AcademicPeriodRepository,
    ClassRepository,
    CourseRepository,
    EnrollmentRepository,
    SubjectRepository,
    TeacherSubjectRepository,
)
from backend.app.repositories.base import BaseRepository
from backend.app.repositories.user_repository import (
    AdministratorRepository,
    StudentRepository,
    TeacherRepository,
    UserRepository,
)


def _session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)()


def test_base_repository_crud_bulk_filters_ordering_and_count():
    engine, db = _session()
    try:
        repository = BaseRepository(Course, db)
        first = repository.create({"code": "CS", "name": "Computer Science"})
        second = repository.create({"code": "MATH", "name": "Mathematics"})
        inactive = repository.create(
            {"code": "ART", "name": "Art", "is_active": False}
        )
        db.commit()

        assert repository.get(first.id) is first
        assert repository.get_by_field("code", "CS") is first
        assert repository.exists(second.id)
        assert repository.get_all(
            filters={"is_active": True, "unknown": "ignored", "name": None},
            order_by="name",
            order_desc=True,
        ) == [second, first]
        assert repository.count(filters={"is_active": True, "invalid": 0}) == 2
        assert repository.count(filters={"is_active": False}) == 1

        updated = repository.update(first.id, {"name": "Computing", "missing": "ignored"})
        assert updated.name == "Computing"
        assert repository.update(first.id, {"name": None}).name == "Computing"
        assert repository.update(uuid4(), {"name": "Missing"}) is None

        created = repository.bulk_create(
            [{"code": "BIO", "name": "Biology"}, {"code": "CHEM", "name": "Chemistry"}]
        )
        updates = [
            {"id": created[0].id, "name": "Biological Science"},
            {"id": uuid4(), "name": "Unknown"},
            {"name": "No id"},
        ]
        assert repository.bulk_update(updates) == 1
        assert created[0].name == "Biological Science"
        assert updates[0] == {"name": "Biological Science"}

        assert repository.delete(second.id)
        assert not repository.exists(second.id)
        assert not repository.delete(uuid4())
        assert inactive.is_active is False
    finally:
        db.close()
        engine.dispose()


def test_user_and_profile_repositories_search_and_filter():
    engine, db = _session()
    try:
        active = User(
            email="active@example.com",
            username="active-user",
            hashed_password="hash",
            full_name="Active Person",
            role=UserRole.STUDENT,
        )
        teacher_user = User(
            email="teacher@example.com",
            username="teacher",
            hashed_password="hash",
            full_name="Teacher Name",
            role=UserRole.TEACHER,
        )
        inactive = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password="hash",
            full_name="Inactive Person",
            role=UserRole.STUDENT,
            is_active=False,
        )
        db.add_all([active, teacher_user, inactive])
        db.flush()
        student = Student(user=active, ra="RA-1")
        teacher = Teacher(user=teacher_user, employee_id="EMP-1")
        db.add_all([student, teacher])
        db.commit()

        users = UserRepository(db)
        assert users.get_by_email(active.email) is active
        assert users.get_by_username(active.username) is active
        assert users.get_by_email_or_username("teacher") is teacher_user
        assert users.get_by_role(UserRole.STUDENT) == [active]
        assert set(users.get_by_role(UserRole.STUDENT, active_only=False)) == {
            active,
            inactive,
        }
        assert users.search("ACTIVE") == [active]
        assert users.search("", UserRole.STUDENT) == [active, inactive]
        assert users.search("teacher", UserRole.STUDENT) == []

        students = StudentRepository(db)
        assert students.get_by_ra("RA-1") is student
        assert students.get_by_user_id(active.id) is student
        assert students.get_by_class(uuid4()) == []
        assert students.get_by_course(uuid4()) == []

        teachers = TeacherRepository(db)
        assert teachers.get_by_employee_id("EMP-1") is teacher
        assert teachers.get_by_user_id(teacher_user.id) is teacher
        assert teachers.get_by_subject(uuid4()) == []
        admins = AdministratorRepository(db)
        assert admins.get_by_employee_id("missing") is None
        assert admins.get_by_user_id(uuid4()) is None
    finally:
        db.close()
        engine.dispose()


def test_academic_repositories_filter_by_status_relationship_and_period():
    engine, db = _session()
    try:
        course = Course(code="CS", name="Computer Science")
        period = AcademicPeriod(
            code="2026",
            name="Year 2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status=AcademicPeriodStatus.ACTIVE,
            is_current=True,
        )
        subject = Subject(code="PY", name="Python", course=course)
        inactive_subject = Subject(
            code="DB",
            name="Databases",
            course=course,
            is_active=False,
        )
        db.add_all([course, period, subject, inactive_subject])
        db.flush()
        teacher_user = User(
            email="teacher2@example.com",
            username="teacher2",
            hashed_password="hash",
            full_name="Teacher Two",
            role=UserRole.TEACHER,
        )
        teacher = Teacher(user=teacher_user, employee_id="EMP-2")
        class_record = Class(
            code="CLS",
            name="Class",
            course=course,
            subject=subject,
            academic_period=period,
            teacher=teacher,
            semester=1,
            year=2026,
        )
        student_user = User(
            email="student@example.com",
            username="student",
            hashed_password="hash",
            full_name="Student",
            role=UserRole.STUDENT,
        )
        student = Student(user=student_user, ra="RA-2")
        other_student_user = User(
            email="student-other@example.com",
            username="student-other",
            hashed_password="hash",
            full_name="Other Student",
            role=UserRole.STUDENT,
        )
        other_student = Student(user=other_student_user, ra="RA-3")
        enrollment = Enrollment(
            student=student,
            class_=class_record,
            academic_period=period,
            status=EnrollmentStatus.ACTIVE,
        )
        inactive_enrollment = Enrollment(
            student=other_student,
            class_=class_record,
            academic_period=period,
            status=EnrollmentStatus.INACTIVE,
        )
        db.add_all(
            [
                teacher,
                class_record,
                student,
                other_student,
                enrollment,
                inactive_enrollment,
            ]
        )
        db.commit()

        courses = CourseRepository(db)
        assert courses.get_by_code("CS") is course
        assert courses.get_active() == [course]
        subjects = SubjectRepository(db)
        assert subjects.get_by_code("PY") is subject
        assert subjects.get_by_course(course.id) == [subject]
        assert set(subjects.get_by_course(course.id, active_only=False)) == {
            subject,
            inactive_subject,
        }

        periods = AcademicPeriodRepository(db)
        assert periods.get_by_code("2026") is period
        assert periods.get_current() is period
        assert periods.get_active() == [period]

        classes = ClassRepository(db)
        assert classes.get_by_code("CLS") is class_record
        assert classes.get_by_teacher(teacher.id) == [class_record]
        assert classes.get_by_course_subject_period(course.id, subject.id, period.id) == [
            class_record
        ]
        assert classes.get_with_details(class_record.id) is class_record
        assert classes.get_students_count(class_record.id) == 1

        enrollments = EnrollmentRepository(db)
        assert enrollments.get_by_student_class(student.id, class_record.id) is enrollment
        assert enrollments.get_by_student_period(student.id, period.id) == [enrollment]
        assert enrollments.get_by_class(class_record.id, EnrollmentStatus.ACTIVE) == [enrollment]
        assert len(enrollments.get_by_class(class_record.id)) == 2

        assignment = TeacherSubject(
            teacher=teacher,
            subject=subject,
            academic_period_id=period.id,
        )
        db.add(assignment)
        db.commit()
        assignments = TeacherSubjectRepository(db)
        assert assignments.get_by_teacher_subject(teacher.id, subject.id, period.id) is assignment
        assert assignments.get_by_teacher_subject(teacher.id, subject.id) is None
        assert assignments.get_by_teacher(teacher.id) == [assignment]

    finally:
        db.close()
        engine.dispose()
