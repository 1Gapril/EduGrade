"""Repository do Módulo Acadêmico."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.academic import (
    AcademicPeriod,
    AcademicPeriodStatus,
    AcademicRule,
    Assessment,
    Attendance,
    Class,
    Course,
    Enrollment,
    EnrollmentStatus,
    Grade,
    Subject,
    TeacherSubject,
)
from backend.app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """Repository para cursos."""

    def __init__(self, db: Session):
        super().__init__(Course, db)

    def get_by_code(self, code: str) -> Course | None:
        """Busca por código."""
        return self.get_by_field("code", code)

    def get_active(self) -> list[Course]:
        """Lista cursos ativos."""
        return self.get_all(filters={"is_active": True})


class SubjectRepository(BaseRepository[Subject]):
    """Repository para disciplinas."""

    def __init__(self, db: Session):
        super().__init__(Subject, db)

    def get_by_code(self, code: str) -> Subject | None:
        """Busca por código."""
        return self.get_by_field("code", code)

    def get_by_course(self, course_id: UUID, active_only: bool = True) -> list[Subject]:
        """Busca disciplinas de um curso."""
        filters = {"course_id": course_id}
        if active_only:
            filters["is_active"] = True
        return self.get_all(filters=filters)


class ClassRepository(BaseRepository[Class]):
    """Repository para turmas."""

    def __init__(self, db: Session):
        super().__init__(Class, db)

    def get_by_code(self, code: str) -> Class | None:
        """Busca por código."""
        return self.get_by_field("code", code)

    def get_by_teacher(self, teacher_id: UUID) -> list[Class]:
        """Busca turmas de um professor."""
        return self.get_all(filters={"teacher_id": teacher_id})

    def get_by_course_subject_period(
        self,
        course_id: UUID,
        subject_id: UUID,
        academic_period_id: UUID
    ) -> list[Class]:
        """Busca turmas por curso, disciplina e período."""
        return self.get_all(filters={
            "course_id": course_id,
            "subject_id": subject_id,
            "academic_period_id": academic_period_id,
        })

    def get_with_details(self, class_id: UUID) -> Class | None:
        """Busca turma com relacionamentos carregados."""
        stmt = select(Class).options(
            joinedload(Class.course),
            joinedload(Class.subject),
            joinedload(Class.academic_period),
            joinedload(Class.teacher).joinedload(Teacher.user),
        ).where(Class.id == class_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_students_count(self, class_id: UUID) -> int:
        """Conta alunos matriculados na turma."""
        from backend.app.models.academic import Enrollment
        stmt = select(func.count(Enrollment.id)).where(
            and_(Enrollment.class_id == class_id, Enrollment.status == EnrollmentStatus.ACTIVE)
        )
        return self.db.execute(stmt).scalar_one()


class AcademicPeriodRepository(BaseRepository[AcademicPeriod]):
    """Repository para períodos letivos."""

    def __init__(self, db: Session):
        super().__init__(AcademicPeriod, db)

    def get_by_code(self, code: str) -> AcademicPeriod | None:
        """Busca por código."""
        return self.get_by_field("code", code)

    def get_current(self) -> AcademicPeriod | None:
        """Busca período atual."""
        return self.get_by_field("is_current", True)

    def get_active(self) -> list[AcademicPeriod]:
        """Lista períodos ativos."""
        return self.get_all(filters={"status": AcademicPeriodStatus.ACTIVE})


class EnrollmentRepository(BaseRepository[Enrollment]):
    """Repository para matrículas."""

    def __init__(self, db: Session):
        super().__init__(Enrollment, db)

    def get_by_student_class(self, student_id: UUID, class_id: UUID) -> Enrollment | None:
        """Busca matrícula de aluno em turma."""
        stmt = select(Enrollment).where(
            and_(Enrollment.student_id == student_id, Enrollment.class_id == class_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_student_period(self, student_id: UUID, academic_period_id: UUID) -> list[Enrollment]:
        """Busca matrículas de aluno em um período."""
        return self.get_all(filters={
            "student_id": student_id,
            "academic_period_id": academic_period_id,
        })

    def get_by_class(self, class_id: UUID, status: EnrollmentStatus | None = None) -> list[Enrollment]:
        """Busca matrículas de uma turma."""
        filters = {"class_id": class_id}
        if status:
            filters["status"] = status
        return self.get_all(filters=filters)


class TeacherSubjectRepository(BaseRepository[TeacherSubject]):
    """Repository para associação professor-disciplina."""

    def __init__(self, db: Session):
        super().__init__(TeacherSubject, db)

    def get_by_teacher_subject(
        self,
        teacher_id: UUID,
        subject_id: UUID,
        academic_period_id: UUID | None = None,
    ) -> TeacherSubject | None:
        """Busca associação professor-disciplina."""
        conditions = [
            TeacherSubject.teacher_id == teacher_id,
            TeacherSubject.subject_id == subject_id,
        ]
        if academic_period_id is None:
            conditions.append(TeacherSubject.academic_period_id.is_(None))
        else:
            conditions.append(TeacherSubject.academic_period_id == academic_period_id)
        stmt = select(TeacherSubject).where(and_(*conditions))
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_teacher(self, teacher_id: UUID) -> list[TeacherSubject]:
        """Busca associações de um professor."""
        return self.get_all(filters={"teacher_id": teacher_id})


class AssessmentRepository(BaseRepository[Assessment]):
    """Repository para avaliações."""

    def __init__(self, db: Session):
        super().__init__(Assessment, db)

    def get_by_class(self, class_id: UUID) -> list[Assessment]:
        """Busca avaliações de uma turma."""
        return self.get_all(filters={"class_id": class_id})

    def get_published(self, class_id: UUID) -> list[Assessment]:
        """Busca avaliações publicadas de uma turma."""
        return self.get_all(filters={"class_id": class_id, "is_published": True})


class GradeRepository(BaseRepository[Grade]):
    """Repository para notas."""

    def __init__(self, db: Session):
        super().__init__(Grade, db)

    def get_by_enrollment_assessment(self, enrollment_id: UUID, assessment_id: UUID) -> Grade | None:
        """Busca nota de matrícula em avaliação."""
        stmt = select(Grade).where(
            and_(Grade.enrollment_id == enrollment_id, Grade.assessment_id == assessment_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_enrollment(self, enrollment_id: UUID) -> list[Grade]:
        """Busca notas de uma matrícula."""
        return self.get_all(filters={"enrollment_id": enrollment_id})

    def get_official_by_enrollment(self, enrollment_id: UUID) -> list[Grade]:
        """Busca notas oficiais de uma matrícula."""
        stmt = select(Grade).where(
            and_(Grade.enrollment_id == enrollment_id, Grade.is_official.is_(True))
        )
        return list(self.db.execute(stmt).scalars().all())

    def calculate_weighted_average(self, enrollment_id: UUID) -> Decimal | None:
        """Calcula média ponderada do aluno."""
        stmt = select(
            func.sum(Grade.score * Assessment.weight) / func.sum(Assessment.weight)
        ).join(Assessment).where(
            and_(Grade.enrollment_id == enrollment_id, Grade.is_official.is_(True))
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        return Decimal(str(result)) if result else None


class AttendanceRepository(BaseRepository[Attendance]):
    """Repository para frequência."""

    def __init__(self, db: Session):
        super().__init__(Attendance, db)

    def get_by_enrollment(self, enrollment_id: UUID) -> list[Attendance]:
        """Busca frequência de uma matrícula."""
        return self.get_all(filters={"enrollment_id": enrollment_id})

    def get_by_class_date(self, class_id: UUID, class_date: date) -> list[Attendance]:
        """Busca frequência de uma turma em uma data."""
        from backend.app.models.academic import Enrollment
        stmt = select(Attendance).join(Enrollment).where(
            and_(Enrollment.class_id == class_id, Attendance.class_date == class_date)
        )
        return list(self.db.execute(stmt).scalars().all())

    def calculate_percentage(self, enrollment_id: UUID) -> Decimal:
        """Calcula porcentagem de frequência."""
        total_stmt = select(func.count(Attendance.id)).where(Attendance.enrollment_id == enrollment_id)
        present_stmt = select(func.count(Attendance.id)).where(
            and_(Attendance.enrollment_id == enrollment_id, Attendance.is_present.is_(True))
        )
        total = self.db.execute(total_stmt).scalar_one()
        present = self.db.execute(present_stmt).scalar_one()
        if total == 0:
            return Decimal("0")
        return Decimal(str(round((present / total) * 100, 2)))


class AcademicRuleRepository(BaseRepository[AcademicRule]):
    """Repository para regras acadêmicas."""

    def __init__(self, db: Session):
        super().__init__(AcademicRule, db)

    def get_by_name(self, name: str) -> AcademicRule | None:
        """Busca por nome."""
        return self.get_by_field("name", name)

    def get_by_type(self, rule_type: str) -> list[AcademicRule]:
        """Busca por tipo."""
        return self.get_all(filters={"rule_type": rule_type, "is_active": True})


# Import para evitar circular
from backend.app.models.user import Teacher  # noqa: E402
