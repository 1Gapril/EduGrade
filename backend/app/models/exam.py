"""Modelos de Provas: Exames, Versões, Questões, Gabaritos, Rubricas, Cópias, Submissões."""

import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from backend.app.models.grading_batch import GradingBatch

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
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class ExamStatus(str, enum.Enum):
    """Status do exame/prova."""
    DRAFT = "draft"
    IN_EDIT = "in_edit"
    AWAITING_VALIDATION = "awaiting_validation"
    PUBLISHED = "published"
    PRINTED = "printed"
    IN_APPLICATION = "in_application"
    AWAITING_CORRECTION = "awaiting_correction"
    IN_CORRECTION = "in_correction"
    AWAITING_REVIEW = "awaiting_review"
    FINALIZED = "finalized"
    CANCELLED = "cancelled"


class QuestionType(str, enum.Enum):
    """Tipo de questão."""
    MULTIPLE_CHOICE = "multiple_choice"
    ESSAY = "essay"
    SHORT_ANSWER = "short_answer"
    CALCULATION = "calculation"
    MULTI_CRITERIA = "multi_criteria"


class PrintStatus(str, enum.Enum):
    """Status de impressão."""
    PENDING = "pending"
    PRINTING = "printing"
    COMPLETED = "completed"
    FAILED = "failed"


class SubmissionStatus(str, enum.Enum):
    """Status da submissão/prova entregue."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    OCR_FAILED = "ocr_failed"
    AWAITING_CORRECTION = "awaiting_correction"
    IN_CORRECTION = "in_correction"
    AWAITING_REVIEW = "awaiting_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"


class Exam(Base):
    """Exame/Prova principal."""

    __tablename__ = "exams"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    total_score: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        default=Decimal("10.00"),
        nullable=False,
    )
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    status: Mapped[ExamStatus] = mapped_column(
        Enum(ExamStatus, native_enum=False),
        default=ExamStatus.DRAFT,
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    print_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
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
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    class_: Mapped["Class"] = relationship("Class", back_populates="exams", lazy="selectin")
    subject: Mapped["Subject"] = relationship(lazy="selectin")
    academic_period: Mapped["AcademicPeriod"] = relationship(lazy="selectin")
    questions: Mapped[list["ExamQuestion"]] = relationship(
        "ExamQuestion",
        back_populates="exam",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    versions: Mapped[list["ExamVersion"]] = relationship(
        "ExamVersion",
        back_populates="exam",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    print_logs: Mapped[list["ExamPrintLog"]] = relationship(
        "ExamPrintLog",
        back_populates="exam",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("total_score > 0", name="ck_exam_total_score_positive"),
        CheckConstraint("duration_minutes > 0", name="ck_exam_duration_positive"),
    )

    def __repr__(self) -> str:
        return f"<Exam(id={self.id}, title={self.title}, status={self.status})>"


class ExamVersion(Base):
    """Versão imutável de uma prova (gerada na publicação)."""

    __tablename__ = "exam_versions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_score: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=False,
    )
    questions_snapshot: Mapped[list] = mapped_column(JSON, nullable=False)
    answer_key_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    rubrics_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    published_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relacionamentos
    exam: Mapped[Exam] = relationship("Exam", back_populates="versions", lazy="selectin")
    copies: Mapped[list["ExamCopy"]] = relationship(
        "ExamCopy",
        back_populates="version",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("exam_id", "version_number", name="uq_exam_version_number"),
    )

    def __repr__(self) -> str:
        return f"<ExamVersion(id={self.id}, exam_id={self.exam_id}, v={self.version_number})>"


class ExamQuestion(Base):
    """Questão de uma prova."""

    __tablename__ = "exam_questions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_order: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, native_enum=False),
        nullable=False,
    )
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=False,
    )
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
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
    exam: Mapped[Exam] = relationship("Exam", back_populates="questions", lazy="selectin")
    answer_key: Mapped["AnswerKey"] = relationship(
        "AnswerKey",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    grading_rubric: Mapped["GradingRubric"] = relationship(
        "GradingRubric",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("exam_id", "question_order", name="uq_exam_question_order"),
        CheckConstraint("score > 0", name="ck_question_score_positive"),
        CheckConstraint("question_order > 0", name="ck_question_order_positive"),
    )

    def __repr__(self) -> str:
        return f"<ExamQuestion(id={self.id}, exam_id={self.exam_id}, question_order={self.question_order}, type={self.type})>"


class AnswerKey(Base):
    """Gabarito de uma questão."""

    __tablename__ = "answer_keys"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    question_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_questions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    accepted_alternatives: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    required_concepts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    partial_scoring: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
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
    question: Mapped[ExamQuestion] = relationship("ExamQuestion", back_populates="answer_key", lazy="selectin")

    def __repr__(self) -> str:
        return f"<AnswerKey(id={self.id}, question_id={self.question_id})>"


class GradingRubric(Base):
    """Rubrica de correção para questões discursivas/calculation."""

    __tablename__ = "grading_rubrics"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    question_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_questions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    criteria: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
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
    question: Mapped[ExamQuestion] = relationship("ExamQuestion", back_populates="grading_rubric", lazy="selectin")

    __table_args__ = (
        CheckConstraint("max_score > 0", name="ck_rubric_max_score_positive"),
    )

    def __repr__(self) -> str:
        return f"<GradingRubric(id={self.id}, question_id={self.question_id})>"


class ExamCopy(Base):
    """Cópia individual de uma prova (para impressão)."""

    __tablename__ = "exam_copies"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    copy_identifier: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    qr_code_data: Mapped[str] = mapped_column(Text, nullable=False)
    student_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_personalized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    printed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    printed_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    version: Mapped[ExamVersion] = relationship("ExamVersion", back_populates="copies", lazy="selectin")
    student: Mapped["Student"] = relationship(lazy="selectin")
    submissions: Mapped[list["ExamSubmission"]] = relationship(
        "ExamSubmission",
        back_populates="copy",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_exam_copies_version_student", "version_id", "student_id"),
    )

    def __repr__(self) -> str:
        return f"<ExamCopy(id={self.id}, identifier={self.copy_identifier})>"


class ExamPrintLog(Base):
    """Log de impressão de provas."""

    __tablename__ = "exam_print_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    printed_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    copy_count: Mapped[int] = mapped_column(Integer, nullable=False)
    copy_identifiers: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[PrintStatus] = mapped_column(
        Enum(PrintStatus, native_enum=False),
        default=PrintStatus.PENDING,
        nullable=False,
    )
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    exam: Mapped[Exam] = relationship("Exam", back_populates="print_logs", lazy="selectin")
    version: Mapped[ExamVersion] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<ExamPrintLog(id={self.id}, exam_id={self.exam_id}, count={self.copy_count})>"


class ExamSubmission(Base):
    """Submissão/Entrega de prova respondida."""

    __tablename__ = "exam_submissions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    copy_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_copies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    batch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("grading_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, native_enum=False),
        default=SubmissionStatus.UPLOADED,
        nullable=False,
        index=True,
    )
    original_files: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    processed_files: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    identified_student_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
    )
    identification_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    manual_identification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
    copy: Mapped[Optional[ExamCopy]] = relationship("ExamCopy", back_populates="submissions", lazy="selectin")
    batch: Mapped[Optional["GradingBatch"]] = relationship("GradingBatch", back_populates="submissions", lazy="selectin")
    version: Mapped[ExamVersion] = relationship(lazy="selectin")
    student: Mapped["Student"] = relationship(
        "Student",
        foreign_keys=[student_id],
        lazy="selectin",
    )
    identified_student: Mapped["Student"] = relationship(
        "Student",
        foreign_keys=[identified_student_id],
        lazy="selectin",
    )
    pages: Mapped[list["SubmissionPage"]] = relationship(
        "SubmissionPage",
        back_populates="submission",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ai_corrections: Mapped[list["AICorrection"]] = relationship(
        "AICorrection",
        back_populates="submission",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ExamSubmission(id={self.id}, copy_id={self.copy_id}, status={self.status})>"


class SubmissionPage(Base):
    """Página individual de uma submissão (página da prova digitalizada)."""

    __tablename__ = "submission_pages"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    submission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    original_image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    processed_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rotation_angle: Mapped[float] = mapped_column(default=0.0, nullable=False)
    perspective_corrected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ocr_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    submission: Mapped[ExamSubmission] = relationship("ExamSubmission", back_populates="pages", lazy="selectin")
    extracted_answers: Mapped[list["ExtractedAnswer"]] = relationship(
        "ExtractedAnswer",
        back_populates="page",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("submission_id", "page_number", name="uq_submission_page_number"),
    )

    def __repr__(self) -> str:
        return f"<SubmissionPage(id={self.id}, submission_id={self.submission_id}, page={self.page_number})>"


class ExtractedAnswer(Base):
    """Resposta extraída de uma página via OCR/IA."""

    __tablename__ = "extracted_answers"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    page_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("submission_pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_order: Mapped[int] = mapped_column(Integer, nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ocr_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    bounding_box: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    page: Mapped[SubmissionPage] = relationship("SubmissionPage", back_populates="extracted_answers", lazy="selectin")
    question: Mapped[ExamQuestion] = relationship(lazy="selectin")

    __table_args__ = (
        Index("ix_extracted_answers_question", "question_id"),
    )

    def __repr__(self) -> str:
        return f"<ExtractedAnswer(id={self.id}, question_id={self.question_id})>"