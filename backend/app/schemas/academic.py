"""Schemas Pydantic para Módulo Acadêmico."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.academic import ACADEMIC_ASSIGNMENT_PERMISSIONS, EnrollmentStatus

# ==================== Course Schemas ====================

class CourseBase(BaseModel):
    """Campos base do curso."""
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    duration_semesters: int = Field(default=8, ge=1, le=20)


class CourseCreate(CourseBase):
    """Schema para criação de curso."""
    pass


class CourseUpdate(BaseModel):
    """Schema para atualização de curso."""
    code: str | None = Field(None, min_length=1, max_length=20)
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    duration_semesters: int | None = Field(None, ge=1, le=20)
    is_active: bool | None = None


class CourseResponse(CourseBase):
    """Schema de resposta do curso."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CourseWithRelations(CourseResponse):
    """Curso com relacionamentos."""
    subjects_count: int = 0
    classes_count: int = 0


# ==================== Subject Schemas ====================

class SubjectBase(BaseModel):
    """Campos base da disciplina."""
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    workload_hours: int = Field(default=60, ge=1)
    credits: int = Field(default=4, ge=1)
    course_id: UUID


class SubjectCreate(SubjectBase):
    """Schema para criação de disciplina."""
    pass


class SubjectUpdate(BaseModel):
    """Schema para atualização de disciplina."""
    code: str | None = Field(None, min_length=1, max_length=20)
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    workload_hours: int | None = Field(None, ge=1)
    credits: int | None = Field(None, ge=1)
    is_active: bool | None = None


class SubjectResponse(SubjectBase):
    """Schema de resposta da disciplina."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SubjectWithCourse(SubjectResponse):
    """Disciplina com curso."""
    course: CourseResponse


# ==================== Class Schemas ====================

class ClassBase(BaseModel):
    """Campos base da turma."""
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    course_id: UUID
    subject_id: UUID
    academic_period_id: UUID
    teacher_id: UUID | None = None
    semester: int = Field(..., ge=1, le=20)
    year: int = Field(..., ge=2000, le=2100)
    schedule: str | None = Field(None, max_length=500)
    classroom: str | None = Field(None, max_length=100)
    max_students: int = Field(default=50, ge=1, le=200)


class ClassCreate(ClassBase):
    """Schema para criação de turma."""
    pass


class ClassUpdate(BaseModel):
    """Schema para atualização de turma."""
    code: str | None = Field(None, min_length=1, max_length=20)
    name: str | None = Field(None, min_length=2, max_length=255)
    teacher_id: UUID | None = None
    schedule: str | None = Field(None, max_length=500)
    classroom: str | None = Field(None, max_length=100)
    max_students: int | None = Field(None, ge=1, le=200)
    is_active: bool | None = None


class ClassResponse(ClassBase):
    """Schema de resposta da turma."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClassWithRelations(ClassResponse):
    """Turma com relacionamentos."""
    course: CourseResponse
    subject: SubjectResponse
    teacher: Optional["TeacherResponse"] = None
    enrollments_count: int = 0


# ==================== Academic Period Schemas ====================

class AcademicPeriodBase(BaseModel):
    """Campos base do período letivo."""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    start_date: date
    end_date: date
    enrollment_start: date | None = None
    enrollment_end: date | None = None


class AcademicPeriodCreate(AcademicPeriodBase):
    """Schema para criação de período letivo."""
    pass


class AcademicPeriodUpdate(BaseModel):
    """Schema para atualização de período letivo."""
    name: str | None = Field(None, min_length=2, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    enrollment_start: date | None = None
    enrollment_end: date | None = None
    status: str | None = None
    is_current: bool | None = None


class AcademicPeriodResponse(AcademicPeriodBase):
    """Schema de resposta do período letivo."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    is_current: bool
    created_at: datetime
    updated_at: datetime


# ==================== Enrollment Schemas ====================

class EnrollmentBase(BaseModel):
    """Campos base da matrícula."""
    student_id: UUID
    class_id: UUID
    academic_period_id: UUID


class EnrollmentCreate(EnrollmentBase):
    """Schema para criação de matrícula."""
    pass


class EnrollmentUpdate(BaseModel):
    """Schema para atualização de matrícula."""
    status: EnrollmentStatus | None = None
    final_grade: Decimal | None = Field(None, ge=0, max_digits=5, decimal_places=2)
    attendance_percentage: Decimal | None = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    situation: str | None = None


class EnrollmentResponse(EnrollmentBase):
    """Schema de resposta da matrícula."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    enrolled_at: datetime
    final_grade: Decimal | None = None
    attendance_percentage: Decimal | None = None
    situation: str | None = None
    created_at: datetime
    updated_at: datetime


class EnrollmentWithRelations(EnrollmentResponse):
    """Matrícula com relacionamentos."""
    student: "StudentResponse"
    class_: ClassResponse


# ==================== TeacherSubject Schemas ====================

class TeacherSubjectBase(BaseModel):
    """Campos base da associação professor-disciplina."""
    teacher_id: UUID
    subject_id: UUID
    academic_period_id: UUID | None = None
    is_coordinator: bool = False


class TeacherSubjectCreate(TeacherSubjectBase):
    """Schema para criação de associação."""
    pass


class TeacherSubjectResponse(TeacherSubjectBase):
    """Schema de resposta."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    assigned_at: datetime
    created_at: datetime


class AcademicAssignmentCreate(BaseModel):
    teacher_id: UUID
    subject_id: UUID
    class_id: UUID
    academic_period_id: UUID
    permissions: dict[str, bool] = Field(default_factory=dict)

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, value: dict[str, bool]) -> dict[str, bool]:
        unknown = set(value) - set(ACADEMIC_ASSIGNMENT_PERMISSIONS)
        if unknown:
            raise ValueError(f"Permissões desconhecidas: {', '.join(sorted(unknown))}")
        return value


class AcademicAssignmentUpdate(BaseModel):
    permissions: dict[str, bool] | None = None
    is_active: bool | None = None

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, value: dict[str, bool] | None) -> dict[str, bool] | None:
        if value is None:
            return None
        unknown = set(value) - set(ACADEMIC_ASSIGNMENT_PERMISSIONS)
        if unknown:
            raise ValueError(f"Permissões desconhecidas: {', '.join(sorted(unknown))}")
        return value


class AcademicAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    teacher_id: UUID
    subject_id: UUID
    class_id: UUID
    academic_period_id: UUID
    permissions: dict[str, bool]
    is_active: bool
    assigned_by: UUID | None
    deactivated_at: datetime | None
    created_at: datetime
    updated_at: datetime


# ==================== Assessment Schemas ====================

class AssessmentBase(BaseModel):
    """Campos base da avaliação."""
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    type: str = Field(..., pattern="^(a1|a2|a3|recovery|final_exam|complementary|custom)$")
    weight: Decimal = Field(default=Decimal("1.00"), ge=0)
    max_score: Decimal = Field(default=Decimal("10.00"), gt=0)
    class_id: UUID
    subject_id: UUID
    academic_period_id: UUID
    scheduled_date: date


class AssessmentCreate(AssessmentBase):
    """Schema para criação de avaliação."""
    pass


class AssessmentUpdate(BaseModel):
    """Schema para atualização de avaliação."""
    title: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    type: str | None = None
    weight: Decimal | None = Field(None, ge=0)
    max_score: Decimal | None = Field(None, gt=0)
    scheduled_date: date | None = None
    is_published: bool | None = None


class AssessmentResponse(AssessmentBase):
    """Schema de resposta da avaliação."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_published: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class AssessmentWithRelations(AssessmentResponse):
    """Avaliação com relacionamentos."""
    class_: ClassResponse
    subject: SubjectResponse


# ==================== Grade Schemas ====================

class GradeBase(BaseModel):
    """Campos base da nota."""
    enrollment_id: UUID
    assessment_id: UUID
    score: Decimal = Field(..., ge=0, max_digits=5, decimal_places=2)


class GradeCreate(GradeBase):
    """Schema para criação de nota."""
    pass


class GradeUpdate(BaseModel):
    """Schema para atualização de nota."""
    score: Decimal | None = Field(None, ge=0, max_digits=5, decimal_places=2)
    is_official: bool | None = None
    notes: str | None = None


class GradeResponse(GradeBase):
    """Schema de resposta da nota."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_official: bool
    graded_by: UUID | None = None
    graded_at: datetime | None = None
    published_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class GradeWithRelations(GradeResponse):
    """Nota com relacionamentos."""
    enrollment: EnrollmentResponse
    assessment: AssessmentResponse


# ==================== Attendance Schemas ====================

class AttendanceBase(BaseModel):
    """Campos base da frequência."""
    enrollment_id: UUID
    class_date: date
    is_present: bool = False
    justified: bool = False
    justification: str | None = None


class AttendanceCreate(AttendanceBase):
    """Schema para criação de frequência."""
    pass


class AttendanceUpdate(BaseModel):
    """Schema para atualização de frequência."""
    is_present: bool | None = None
    justified: bool | None = None
    justification: str | None = None


class AttendanceResponse(AttendanceBase):
    """Schema de resposta da frequência."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recorded_by: UUID
    created_at: datetime
    updated_at: datetime


# ==================== Academic Rule Schemas ====================

class AcademicRuleBase(BaseModel):
    """Campos base da regra acadêmica."""
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    rule_type: str = Field(..., min_length=1, max_length=50)
    config: str  # JSON string


class AcademicRuleCreate(AcademicRuleBase):
    """Schema para criação de regra."""
    pass


class AcademicRuleUpdate(BaseModel):
    """Schema para atualização de regra."""
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None
    rule_type: str | None = None
    config: str | None = None
    is_active: bool | None = None


class AcademicRuleResponse(AcademicRuleBase):
    """Schema de resposta da regra."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==================== Bulk Operations ====================

class BulkEnrollmentCreate(BaseModel):
    """Criação em lote de matrículas."""
    class_id: UUID
    academic_period_id: UUID
    student_ids: list[UUID]


class BulkGradeCreate(BaseModel):
    """Criação em lote de notas."""
    assessment_id: UUID
    grades: list[GradeCreate]


class BulkAttendanceCreate(BaseModel):
    """Criação em lote de frequência."""
    class_id: UUID
    class_date: date
    attendances: list[AttendanceCreate]


# ==================== Consultas do próprio aluno ====================

class MyAttendanceRecord(BaseModel):
    """Registro individual de frequência do aluno autenticado."""

    date: date
    is_present: bool
    justified: bool
    justification: str | None = None


class MyAttendanceSummary(BaseModel):
    """Resumo de frequência por matrícula do aluno autenticado."""

    enrollment_id: UUID
    class_id: UUID
    class_code: str
    class_name: str
    subject_name: str
    total_classes: int
    present_count: int
    absent_count: int
    justified_count: int
    percentage: Decimal
    records: list[MyAttendanceRecord]


class MyScheduleItem(BaseModel):
    """Item da grade horária do aluno autenticado."""

    class_id: UUID
    class_code: str
    class_name: str
    subject_name: str
    course_name: str
    teacher_name: str | None = None
    schedule: str | None = None
    classroom: str | None = None
    semester: int
    year: int
    period_name: str | None = None


# Forward references
from backend.app.schemas.user import StudentResponse, TeacherResponse  # noqa: E402

ClassWithRelations.model_rebuild()
EnrollmentWithRelations.model_rebuild()
