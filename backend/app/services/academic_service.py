"""Service do Módulo Acadêmico."""

from typing import Optional, List
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.academic import (
    Course, Subject, Class, AcademicPeriod, AcademicPeriodStatus,
    Enrollment, EnrollmentStatus, TeacherSubject,
    Assessment, AssessmentType, Grade, Attendance, AcademicRule
)
from backend.app.repositories.academic_repository import (
    CourseRepository, SubjectRepository, ClassRepository,
    AcademicPeriodRepository, EnrollmentRepository,
    TeacherSubjectRepository, AssessmentRepository,
    GradeRepository, AttendanceRepository, AcademicRuleRepository
)
from backend.app.schemas.academic import (
    CourseCreate, CourseUpdate,
    SubjectCreate, SubjectUpdate,
    ClassCreate, ClassUpdate,
    AcademicPeriodCreate, AcademicPeriodUpdate,
    EnrollmentCreate, EnrollmentUpdate,
    TeacherSubjectCreate,
    AssessmentCreate, AssessmentUpdate,
    GradeCreate, GradeUpdate,
    AttendanceCreate, AttendanceUpdate,
    AcademicRuleCreate, AcademicRuleUpdate,
)
from backend.app.core.exceptions import ValidationError, NotFoundError, ConflictError
from backend.app.repositories.ai_correction_repository import AuditLogRepository, AuditActionType


class CourseService:
    """Serviço de cursos."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CourseRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, course_data: CourseCreate, created_by: UUID) -> Course:
        if self.repo.get_by_code(course_data.code):
            raise ConflictError("Código do curso já existe")
        course = Course(**course_data.model_dump())
        self.db.add(course)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, f"Curso criado: {course.code}", created_by,
                          "Course", course.id, new_values=course_data.model_dump())
        return course

    def get(self, course_id: UUID) -> Course:
        course = self.repo.get(course_id)
        if not course:
            raise NotFoundError("Curso não encontrado")
        return course

    def update(self, course_id: UUID, course_data: CourseUpdate, updated_by: UUID) -> Course:
        course = self.get(course_id)
        old = {"code": course.code, "name": course.name, "is_active": course.is_active}
        for k, v in course_data.model_dump(exclude_unset=True).items():
            setattr(course, k, v)
        course.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.audit_repo.log(AuditActionType.UPDATE, f"Curso atualizado: {course.code}", updated_by,
                          "Course", course.id, old_values=old, new_values=course_data.model_dump(exclude_unset=True))
        return course

    def list(self, active_only: bool = True) -> List[Course]:
        return self.repo.get_active() if active_only else self.repo.get_all()


class SubjectService:
    """Serviço de disciplinas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = SubjectRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, subject_data: SubjectCreate, created_by: UUID) -> Subject:
        if self.repo.get_by_code(subject_data.code):
            raise ConflictError("Código da disciplina já existe")
        subject = Subject(**subject_data.model_dump())
        self.db.add(subject)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, f"Disciplina criada: {subject.code}", created_by,
                          "Subject", subject.id, new_values=subject_data.model_dump())
        return subject

    def get(self, subject_id: UUID) -> Subject:
        subject = self.repo.get(subject_id)
        if not subject:
            raise NotFoundError("Disciplina não encontrada")
        return subject

    def get_by_course(self, course_id: UUID) -> List[Subject]:
        return self.repo.get_by_course(course_id)

    def update(self, subject_id: UUID, subject_data: SubjectUpdate, updated_by: UUID) -> Subject:
        subject = self.get(subject_id)
        for k, v in subject_data.model_dump(exclude_unset=True).items():
            setattr(subject, k, v)
        subject.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.audit_repo.log(AuditActionType.UPDATE, f"Disciplina atualizada: {subject.code}", updated_by,
                          "Subject", subject.id, new_values=subject_data.model_dump(exclude_unset=True))
        return subject


class ClassService:
    """Serviço de turmas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ClassRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, class_data: ClassCreate, created_by: UUID) -> Class:
        cls = Class(**class_data.model_dump())
        self.db.add(cls)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, f"Turma criada: {cls.code}", created_by,
                          "Class", cls.id, new_values=class_data.model_dump())
        return cls

    def get(self, class_id: UUID) -> Class:
        cls = self.repo.get_with_details(class_id)
        if not cls:
            raise NotFoundError("Turma não encontrada")
        return cls

    def get_by_teacher(self, teacher_id: UUID) -> List[Class]:
        return self.repo.get_by_teacher(teacher_id)

    def update(self, class_id: UUID, class_data: ClassUpdate, updated_by: UUID) -> Class:
        cls = self.get(class_id)
        for k, v in class_data.model_dump(exclude_unset=True).items():
            setattr(cls, k, v)
        cls.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.audit_repo.log(AuditActionType.UPDATE, f"Turma atualizada: {cls.code}", updated_by,
                          "Class", cls.id, new_values=class_data.model_dump(exclude_unset=True))
        return cls

    def get_students_count(self, class_id: UUID) -> int:
        return self.repo.get_students_count(class_id)


class AcademicPeriodService:
    """Serviço de períodos letivos."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AcademicPeriodRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, period_data: AcademicPeriodCreate, created_by: UUID) -> AcademicPeriod:
        if self.repo.get_by_code(period_data.code):
            raise ConflictError("Código do período já existe")
        period = AcademicPeriod(**period_data.model_dump())
        self.db.add(period)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, f"Período criado: {period.code}", created_by,
                          "AcademicPeriod", period.id, new_values=period_data.model_dump())
        return period

    def get(self, period_id: UUID) -> AcademicPeriod:
        period = self.repo.get(period_id)
        if not period:
            raise NotFoundError("Período não encontrado")
        return period

    def get_current(self) -> Optional[AcademicPeriod]:
        return self.repo.get_current()

    def set_current(self, period_id: UUID, updated_by: UUID) -> AcademicPeriod:
        """Define período como atual."""
        # Unset current
        current = self.repo.get_current()
        if current:
            current.is_current = False
        period = self.get(period_id)
        period.is_current = True
        period.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.audit_repo.log(AuditActionType.UPDATE, f"Período atual definido: {period.code}", updated_by,
                          "AcademicPeriod", period.id)
        return period


class EnrollmentService:
    """Serviço de matrículas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = EnrollmentRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, enrollment_data: EnrollmentCreate, created_by: UUID) -> Enrollment:
        if self.repo.get_by_student_class(enrollment_data.student_id, enrollment_data.class_id):
            raise ConflictError("Aluno já matriculado nesta turma")
        enrollment = Enrollment(**enrollment_data.model_dump())
        self.db.add(enrollment)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, "Matrícula criada", created_by,
                          "Enrollment", enrollment.id, new_values=enrollment_data.model_dump())
        return enrollment

    def bulk_create(self, class_id: UUID, student_ids: List[UUID], academic_period_id: UUID, created_by: UUID) -> List[Enrollment]:
        """Matrícula em lote."""
        enrollments = []
        for student_id in student_ids:
            existing = self.repo.get_by_student_class(student_id, class_id)
            if not existing:
                e = Enrollment(
                    student_id=student_id,
                    class_id=class_id,
                    academic_period_id=academic_period_id,
                    status=EnrollmentStatus.ACTIVE,
                )
                self.db.add(e)
                enrollments.append(e)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, f"Matrículas em lote: {len(enrollments)} criadas", created_by,
                          "Enrollment", None, new_values={"count": len(enrollments), "class_id": str(class_id)})
        return enrollments

    def get(self, enrollment_id: UUID) -> Enrollment:
        enrollment = self.repo.get(enrollment_id)
        if not enrollment:
            raise NotFoundError("Matrícula não encontrada")
        return enrollment

    def update(self, enrollment_id: UUID, enrollment_data: EnrollmentUpdate, updated_by: UUID) -> Enrollment:
        enrollment = self.get(enrollment_id)
        for k, v in enrollment_data.model_dump(exclude_unset=True).items():
            setattr(enrollment, k, v)
        enrollment.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return enrollment

    def get_by_student(self, student_id: UUID, academic_period_id: UUID) -> List[Enrollment]:
        return self.repo.get_by_student_period(student_id, academic_period_id)


class AssessmentService:
    """Serviço de avaliações."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AssessmentRepository(db)
        self.grade_repo = GradeRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, assessment_data: AssessmentCreate, created_by: UUID) -> Assessment:
        assessment = Assessment(**assessment_data.model_dump(), created_by=created_by)
        self.db.add(assessment)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, f"Avaliação criada: {assessment.title}", created_by,
                          "Assessment", assessment.id, new_values=assessment_data.model_dump())
        return assessment

    def get(self, assessment_id: UUID) -> Assessment:
        assessment = self.repo.get(assessment_id)
        if not assessment:
            raise NotFoundError("Avaliação não encontrada")
        return assessment

    def publish(self, assessment_id: UUID, published_by: UUID) -> Assessment:
        assessment = self.get(assessment_id)
        assessment.is_published = True
        self.db.flush()
        self.audit_repo.log(AuditActionType.UPDATE, f"Avaliação publicada: {assessment.title}", published_by,
                          "Assessment", assessment.id, new_values={"is_published": True})
        return assessment

    def calculate_final_grade(self, enrollment_id: UUID) -> Optional[Decimal]:
        return self.grade_repo.calculate_weighted_average(enrollment_id)


class GradeService:
    """Serviço de notas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = GradeRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, grade_data: GradeCreate, graded_by: UUID) -> Grade:
        existing = self.repo.get_by_enrollment_assessment(grade_data.enrollment_id, grade_data.assessment_id)
        if existing:
            raise ConflictError("Nota já existe para esta matrícula e avaliação")
        grade = Grade(**grade_data.model_dump(), graded_by=graded_by, graded_at=datetime.now(timezone.utc))
        self.db.add(grade)
        self.db.flush()
        self.audit_repo.log(AuditActionType.CREATE, "Nota criada", graded_by,
                          "Grade", grade.id, new_values=grade_data.model_dump())
        return grade

    def update(self, grade_id: UUID, grade_data: GradeUpdate, updated_by: UUID) -> Grade:
        grade = self.repo.get(grade_id)
        if not grade:
            raise NotFoundError("Nota não encontrada")
        old = {"score": str(grade.score), "is_official": grade.is_official}
        for k, v in grade_data.model_dump(exclude_unset=True).items():
            setattr(grade, k, v)
        grade.updated_at = datetime.now(timezone.utc)
        if grade_data.is_official and not grade.is_official:
            grade.published_at = datetime.now(timezone.utc)
        self.db.flush()
        self.audit_repo.log(AuditActionType.GRADE_CHANGE, "Nota atualizada", updated_by,
                          "Grade", grade.id, old_values=old, new_values=grade_data.model_dump(exclude_unset=True))
        return grade

    def publish(self, grade_id: UUID, published_by: UUID) -> Grade:
        grade = self.repo.get(grade_id)
        if not grade:
            raise NotFoundError("Nota não encontrada")
        grade.is_official = True
        grade.published_at = datetime.now(timezone.utc)
        self.db.flush()
        self.audit_repo.log(AuditActionType.GRADE_PUBLISH, "Nota publicada", published_by,
                          "Grade", grade.id)
        return grade


class AttendanceService:
    """Serviço de frequência."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AttendanceRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, attendance_data: AttendanceCreate, recorded_by: UUID) -> Attendance:
        existing = self.repo.get_by_enrollment(attendance_data.enrollment_id)
        for e in existing:
            if e.class_date == attendance_data.class_date:
                raise ConflictError("Frequência já registrada para esta data")
        attendance = Attendance(**attendance_data.model_dump(), recorded_by=recorded_by)
        self.db.add(attendance)
        self.db.flush()
        return attendance

    def bulk_create(self, class_id: UUID, class_date: date, attendances: List[AttendanceCreate], recorded_by: UUID) -> List[Attendance]:
        """Frequência em lote."""
        records = []
        for a in attendances:
            existing = self.repo.get_by_enrollment(a.enrollment_id)
            if not any(e.class_date == class_date for e in existing):
                att = Attendance(**a.model_dump(), recorded_by=recorded_by)
                self.db.add(att)
                records.append(att)
        self.db.flush()
        return records

    def calculate_percentage(self, enrollment_id: UUID) -> Decimal:
        return self.repo.calculate_percentage(enrollment_id)


class TeacherSubjectService:
    """Serviço de associação professor-disciplina."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = TeacherSubjectRepository(db)

    def create(self, data: TeacherSubjectCreate) -> TeacherSubject:
        existing = self.repo.get_by_teacher_subject(data.teacher_id, data.subject_id)
        if existing:
            raise ConflictError("Associação já existe")
        ts = TeacherSubject(**data.model_dump())
        self.db.add(ts)
        self.db.flush()
        return ts


class AcademicRuleService:
    """Serviço de regras acadêmicas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AcademicRuleRepository(db)

    def create(self, rule_data: AcademicRuleCreate) -> AcademicRule:
        if self.repo.get_by_name(rule_data.name):
            raise ConflictError("Nome da regra já existe")
        rule = AcademicRule(**rule_data.model_dump())
        self.db.add(rule)
        self.db.flush()
        return rule

    def get_by_type(self, rule_type: str) -> List[AcademicRule]:
        return self.repo.get_by_type(rule_type)