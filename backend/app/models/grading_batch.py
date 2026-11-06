"""Modelos para Processamento em Lote (Grading Batches) - ADENDO OFICIAL."""

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.models.exam import ExamSubmission
    from backend.app.models.user import Student


class BatchStatus(str, enum.Enum):
    """Status do lote de correção."""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSING_PAGES = "processing_pages"
    IDENTIFYING = "identifying"
    GROUPING = "grouping"
    GRADING = "grading"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileStatus(str, enum.Enum):
    """Status de cada arquivo no lote."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PageGroupStatus(str, enum.Enum):
    """Status do agrupamento de páginas."""
    PENDING = "pending"
    GROUPED = "grouped"
    CONFLICT = "conflict"
    MANUAL_REVIEW = "manual_review"


class IdentificationStatus(str, enum.Enum):
    """Status da identificação do aluno."""
    IDENTIFIED = "identified"
    PENDING = "pending"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    MANUAL = "manual"


class GradingBatch(Base):
    """Lote de provas enviado pelo professor para processamento."""

    __tablename__ = "grading_batches"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    uploaded_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[BatchStatus] = mapped_column(
        Enum(BatchStatus, native_enum=False),
        default=BatchStatus.UPLOADING,
        nullable=False,
        index=True,
    )
    total_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_pages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    identified_students: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    grouped_submissions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    graded_submissions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pending_review: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
    files: Mapped[list["GradingBatchFile"]] = relationship(
        "GradingBatchFile",
        back_populates="batch",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    submissions: Mapped[list["ExamSubmission"]] = relationship(
        "ExamSubmission",
        back_populates="batch",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<GradingBatch(id={self.id}, exam_id={self.exam_id}, status={self.status})>"


class GradingBatchFile(Base):
    """Arquivo individual dentro de um lote."""

    __tablename__ = "grading_batch_files"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    batch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("grading_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # image, pdf
    page_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, native_enum=False),
        default=FileStatus.PENDING,
        nullable=False,
    )
    processed_pages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    batch: Mapped[GradingBatch] = relationship("GradingBatch", back_populates="files", lazy="selectin")
    pages: Mapped[list["ExamSubmissionPage"]] = relationship(
        "ExamSubmissionPage",
        back_populates="batch_file",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<GradingBatchFile(id={self.id}, filename={self.original_filename}, status={self.status})>"


class ExamSubmissionPage(Base):
    """Página individual de uma submissão (estendida para batches)."""

    __tablename__ = "exam_submission_pages"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    batch_file_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("grading_batch_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submission_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_submissions.id", ondelete="SET NULL"),
        nullable=True,
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
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    batch_file: Mapped[GradingBatchFile] = relationship("GradingBatchFile", back_populates="pages", lazy="selectin")
    submission: Mapped[Optional["ExamSubmission"]] = relationship("ExamSubmission", lazy="selectin")
    identification_results: Mapped[list["StudentIdentificationResult"]] = relationship(
        "StudentIdentificationResult",
        back_populates="page",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_submission_pages_batch_file", "batch_file_id"),
    )

    def __repr__(self) -> str:
        return f"<ExamSubmissionPage(id={self.id}, batch_file_id={self.batch_file_id}, page={self.page_number})>"


class StudentIdentificationResult(Base):
    """Resultado da identificação de aluno por IA."""

    __tablename__ = "student_identification_results"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    page_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_submission_pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submission_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_submissions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    identified_ra: Mapped[str | None] = mapped_column(String(50), nullable=True)
    identified_matricula: Mapped[str | None] = mapped_column(String(50), nullable=True)
    identified_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    identified_exam_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    identified_class_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    identified_copy_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    matched_student_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ra_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    matricula_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    match_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ra_only, matricula_only, both, name_fallback
    status: Mapped[IdentificationStatus] = mapped_column(
        Enum(IdentificationStatus, native_enum=False),
        default=IdentificationStatus.PENDING,
        nullable=False,
    )
    conflict_details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    manual_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    overridden_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    overridden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    ai_model: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_response: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    page: Mapped[ExamSubmissionPage] = relationship("ExamSubmissionPage", back_populates="identification_results", lazy="selectin")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")
    submission: Mapped["ExamSubmission"] = relationship("ExamSubmission", lazy="selectin")

    def __repr__(self) -> str:
        return f"<StudentIdentificationResult(id={self.id}, ra={self.identified_ra}, status={self.status})>"


class ExamPageGroup(Base):
    """Agrupamento de páginas pertencentes à mesma prova."""

    __tablename__ = "exam_page_groups"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    batch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("grading_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="RESTRICT"),
        nullable=False,
    )
    version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    copy_identifier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    page_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[PageGroupStatus] = mapped_column(
        Enum(PageGroupStatus, native_enum=False),
        default=PageGroupStatus.PENDING,
        nullable=False,
    )
    confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    conflict_details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_submission_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_submissions.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    batch: Mapped[GradingBatch] = relationship(lazy="selectin")
    student: Mapped["Student"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<ExamPageGroup(id={self.id}, student_id={self.student_id}, pages={len(self.page_ids)})>"


class GradingAuditLog(Base):
    """Log de auditoria específico do processamento de correção."""

    __tablename__ = "grading_audit_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    batch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("grading_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submission_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_submissions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    performed_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    ai_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    success: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("ix_grading_audit_batch_action", "batch_id", "action"),
    )

    def __repr__(self) -> str:
        return f"<GradingAuditLog(id={self.id}, action={self.action}, entity={self.entity_type})>"
