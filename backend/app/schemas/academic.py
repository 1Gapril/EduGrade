"""Schemas Pydantic para Módulo Acadêmico."""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# ==================== Course Schemas ====================

class CourseBase(BaseModel):
    """Campos base do curso."""
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    duration_semesters: int = Field(default=8, ge=1, le=20)


class CourseCreate(CourseBase):
    """Schema para criação de curso."""
    pass


class CourseUpdate(BaseModel):
    """Schema para atualização de curso."""
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    duration_semesters: Optional[int] = Field(None, ge=1, le=20)
    is_active: Optional[bool] = None


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
    description: Optional[str] = None
    workload_hours: int = Field(default=60, ge=1)
    credits: int = Field(default=4, ge=1)
    course_id: UUID


class SubjectCreate(SubjectBase):
    """Schema para criação de disciplina."""
    pass


class SubjectUpdate(BaseModel):
    """Schema para atualização de disciplina."""
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    workload_hours: Optional[int] = Field(None, ge=1)
    credits: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


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
    teacher_id: Optional[UUID] = None
    semester: int = Field(..., ge=1, le=20)
    year: int = Field(..., ge=2000, le=2100)
    schedule: Optional[str] = Field(None, max_length=500)
    classroom: Optional[str] = Field(None, max_length=100)
    max_students: int = Field(default=50, ge=1, le=200)


class ClassCreate(ClassBase):
    """Schema para criação de turma."""
    pass


class ClassUpdate(BaseModel):
    """Schema para atualização de turma."""
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    teacher_id: Optional[UUID] = None
    schedule: Optional[str] = Field(None, max_length=500)
    classroom: Optional[str] = Field(None, max_length=100)
    max_students: Optional[int] = Field(None, ge=1, le=200)
    is_active: Optional[bool] = None


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
    enrollment_start: Optional[date] = None
    enrollment_end: Optional[date] = None


class AcademicPeriodCreate(AcademicPeriodBase):
    """Schema para criação de período letivo."""
    pass


class AcademicPeriodUpdate(BaseModel):
    """Schema para atualização de período letivo."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    enrollment_start: Optional[date] = None
    enrollment_end: Optional[date] = None
    status: Optional[str] = None
    is_current: Optional[bool] = None


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
    status: Optional[str] = None
    final_grade: Optional[Decimal] = Field(None, ge=0, max_digits=5, decimal_places=2)
    attendance_percentage: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    situation: Optional[str] = None


class EnrollmentResponse(EnrollmentBase):
    """Schema de resposta da matrícula."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    enrolled_at: datetime
    final_grade: Optional[Decimal] = None
    attendance_percentage: Optional[Decimal] = None
    situation: Optional[str] = None
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
    academic_period_id: Optional[UUID] = None
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


# ==================== Assessment Schemas ====================

class AssessmentBase(BaseModel):
    """Campos base da avaliação."""
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
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
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = None
    weight: Optional[Decimal] = Field(None, ge=0)
    max_score: Optional[Decimal] = Field(None, gt=0)
    scheduled_date: Optional[date] = None
    is_published: Optional[bool] = None


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
    score: Optional[Decimal] = Field(None, ge=0, max_digits=5, decimal_places=2)
    is_official: Optional[bool] = None
    notes: Optional[str] = None


class GradeResponse(GradeBase):
    """Schema de resposta da nota."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_official: bool
    graded_by: Optional[UUID] = None
    graded_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    notes: Optional[str] = None
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
    justification: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    """Schema para criação de frequência."""
    pass


class AttendanceUpdate(BaseModel):
    """Schema para atualização de frequência."""
    is_present: Optional[bool] = None
    justified: Optional[bool] = None
    justification: Optional[str] = None


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
    description: Optional[str] = None
    rule_type: str = Field(..., min_length=1, max_length=50)
    config: str  # JSON string


class AcademicRuleCreate(AcademicRuleBase):
    """Schema para criação de regra."""
    pass


class AcademicRuleUpdate(BaseModel):
    """Schema para atualização de regra."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    rule_type: Optional[str] = None
    config: Optional[str] = None
    is_active: Optional[bool] = None


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
    student_ids: List[UUID]


class BulkGradeCreate(BaseModel):
    """Criação em lote de notas."""
    assessment_id: UUID
    grades: List[GradeCreate]


class BulkAttendanceCreate(BaseModel):
    """Criação em lote de frequência."""
    class_id: UUID
    class_date: date
    attendances: List[AttendanceCreate]


# Forward references
from backend.app.schemas.user import StudentResponse, TeacherResponse
ClassWithRelations.model_rebuild()
EnrollmentWithRelations.model_rebuild()