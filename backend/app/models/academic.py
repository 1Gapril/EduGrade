"""Modelos Acadêmicos: Cursos, Disciplinas, Turmas, Matrículas, Períodos, Avaliações, Notas, Frequência."""

import enum
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.models.user import Student, Teacher


class AcademicPeriodStatus(str, enum.Enum):
    """Status do período letivo."""
    PLANNED = "planned"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class EnrollmentStatus(str, enum.Enum):
    """Status da matrícula."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSFERRED = "transferred"
    GRADUATED = "graduated"
    DROPPED = "dropped"
    SUSPENDED = "suspended"


class AssessmentType(str, enum.Enum):
    """Tipo de avaliação."""
    A1 = "a1"
    A2 = "a2"
    A3 = "a3"
    RECOVERY = "recovery"
    FINAL_EXAM = "final_exam"
    COMPLEMENTARY = "complementary"
    CUSTOM = "custom"


class Course(Base):
    """Curso acadêmico."""

    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_semesters: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    classes: Mapped[list["Class"]] = relationship(
        "Class",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, code={self.code}, name={self.name})>"


class Subject(Base):
    """Disciplina/Matéria."""

    __tablename__ = "subjects"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    workload_hours: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    course: Mapped[Course] = relationship("Course", back_populates="subjects", lazy="selectin")
    classes: Mapped[list["Class"]] = relationship(
        "Class",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    teacher_subjects: Mapped[list["TeacherSubject"]] = relationship(
        "TeacherSubject",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("code", "course_id", name="uq_subject_code_course"),
    )

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, code={self.code}, name={self.name})>"


class Class(Base):
    """Turma."""

    __tablename__ = "classes"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    academic_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("academic_periods.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    schedule: Mapped[str | None] = mapped_column(String(500), nullable=True)
    classroom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    max_students: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    course: Mapped[Course] = relationship("Course", back_populates="classes", lazy="selectin")
    subject: Mapped[Subject] = relationship("Subject", back_populates="classes", lazy="selectin")
    academic_period: Mapped["AcademicPeriod"] = relationship(
        "AcademicPeriod",
        back_populates="classes",
        lazy="selectin",
    )
    teacher: Mapped["Teacher"] = relationship("Teacher", lazy="selectin")
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="class_",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment",
        back_populates="class_",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    exams: Mapped[list["Exam"]] = relationship(
        "Exam",
        back_populates="class_",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("course_id", "subject_id", "academic_period_id", "code", name="uq_class_unique"),
        CheckConstraint("max_students > 0", name="ck_class_max_students_positive"),
    )

    def __repr__(self) -> str:
        return f"<Class(id={self.id}, code={self.code}, name={self.name})>"


class AcademicPeriod(Base):
    """Período letivo."""

    __tablename__ = "academic_periods"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    enrollment_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    enrollment_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[AcademicPeriodStatus] = mapped_column(
        Enum(AcademicPeriodStatus, native_enum=False),
        default=AcademicPeriodStatus.PLANNED,
        nullable=False,
    )
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    classes: Mapped[list[Class]] = relationship(
        "Class",
        back_populates="academic_period",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="academic_period",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_period_dates_valid"),
    )

    def __repr__(self) -> str:
        return f"<AcademicPeriod(id={self.id}, code={self.code}, status={self.status})>"


class Enrollment(Base):
    """Matrícula de aluno em turma."""

    __tablename__ = "enrollments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    class_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    academic_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("academic_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus, native_enum=False),
        default=EnrollmentStatus.ACTIVE,
        nullable=False,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    final_grade: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    attendance_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    situation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    student: Mapped["Student"] = relationship("Student", back_populates="enrollments", lazy="selectin")
    class_: Mapped["Class"] = relationship("Class", back_populates="enrollments", lazy="selectin")
    academic_period: Mapped[AcademicPeriod] = relationship(
        "AcademicPeriod",
        back_populates="enrollments",
        lazy="selectin",
    )
    grades: Mapped[list["Grade"]] = relationship(
        "Grade",
        back_populates="enrollment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attendance_records: Mapped[list["Attendance"]] = relationship(
        "Attendance",
        back_populates="enrollment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("student_id", "class_id", name="uq_enrollment_student_class"),
        Index("ix_enrollment_student_period", "student_id", "academic_period_id"),
    )

    def __repr__(self) -> str:
        return f"<Enrollment(id={self.id}, student_id={self.student_id}, class_id={self.class_id})>"


class TeacherSubject(Base):
    """Associação Professor-Disciplina (autorização para lecionar)."""

    __tablename__ = "teacher_subjects"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    teacher_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    academic_period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("academic_periods.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_coordinator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="teacher_subjects", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="teacher_subjects", lazy="selectin")
    academic_period: Mapped[AcademicPeriod | None] = relationship(lazy="selectin")

    __table_args__ = (
        UniqueConstraint("teacher_id", "subject_id", "academic_period_id", name="uq_teacher_subject_period"),
    )

    def __repr__(self) -> str:
        return f"<TeacherSubject(teacher_id={self.teacher_id}, subject_id={self.subject_id})>"


class Assessment(Base):
    """Avaliação (prova, trabalho, etc.)."""

    __tablename__ = "assessments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[AssessmentType] = mapped_column(
        Enum(AssessmentType, native_enum=False),
        nullable=False,
    )
    weight: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        default=Decimal("1.00"),
        nullable=False,
    )
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        default=Decimal("10.00"),
        nullable=False,
    )
    class_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    academic_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("academic_periods.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    class_: Mapped[Class] = relationship("Class", back_populates="assessments", lazy="selectin")
    subject: Mapped[Subject] = relationship("Subject", back_populates="assessments", lazy="selectin")
    academic_period: Mapped[AcademicPeriod] = relationship(lazy="selectin")
    grades: Mapped[list["Grade"]] = relationship(
        "Grade",
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("weight > 0", name="ck_assessment_weight_positive"),
        CheckConstraint("max_score > 0", name="ck_assessment_max_score_positive"),
    )

    def __repr__(self) -> str:
        return f"<Assessment(id={self.id}, title={self.title}, type={self.type})>"


class Grade(Base):
    """Nota de aluno em avaliação."""

    __tablename__ = "grades"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    enrollment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=False,
    )
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    graded_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    enrollment: Mapped[Enrollment] = relationship("Enrollment", back_populates="grades", lazy="selectin")
    assessment: Mapped[Assessment] = relationship("Assessment", back_populates="grades", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("enrollment_id", "assessment_id", name="uq_grade_enrollment_assessment"),
        CheckConstraint("score >= 0", name="ck_grade_score_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<Grade(id={self.id}, score={self.score}, official={self.is_official})>"


class Attendance(Base):
    """Registro de frequência."""

    __tablename__ = "attendance"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    enrollment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    class_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    justified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    enrollment: Mapped[Enrollment] = relationship("Enrollment", back_populates="attendance_records", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("enrollment_id", "class_date", name="uq_attendance_enrollment_date"),
    )

    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, present={self.is_present}, date={self.class_date})>"


class AcademicRule(Base):
    """Regras acadêmicas configuráveis."""

    __tablename__ = "academic_rules"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # approval, recovery, final_exam, etc.
    config: Mapped[str] = mapped_column(Text, nullable=False)  # JSON com configurações
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<AcademicRule(id={self.id}, name={self.name}, type={self.rule_type})>"