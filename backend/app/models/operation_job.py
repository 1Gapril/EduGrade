"""Modelo de tarefas de longa duração (barra global de progresso)."""

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class OperationKind(str, enum.Enum):
    """Tipos de operação acompanhadas pela barra global."""

    EXAM_PDF_IMPORT = "exam_pdf_import"
    SUBMISSION_UPLOAD = "submission_upload"
    AI_CORRECTION = "ai_correction"
    STUDENT_IMPORT = "student_import"
    GRADE_IMPORT = "grade_import"
    QUALITY_RUN = "quality_run"


class OperationStatus(str, enum.Enum):
    """Estados possíveis de uma operação."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    SUCCEEDED_WITH_WARNINGS = "succeeded_with_warnings"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_STATUSES = {
    OperationStatus.SUCCEEDED,
    OperationStatus.SUCCEEDED_WITH_WARNINGS,
    OperationStatus.FAILED,
    OperationStatus.CANCELLED,
}


class OperationJob(Base):
    """Estado oficial do progresso de uma operação do EduGrade.

    O backend é a fonte da verdade: o frontend apenas consulta este registro.
    ``progress`` é ``None`` quando a etapa não tem como ser medida (indicador
    indeterminado).
    """

    __tablename__ = "operation_jobs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    kind: Mapped[OperationKind] = mapped_column(
        Enum(OperationKind, native_enum=False),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[OperationStatus] = mapped_column(
        Enum(OperationStatus, native_enum=False),
        nullable=False,
        default=OperationStatus.PENDING,
        index=True,
    )

    step_key: Mapped[str | None] = mapped_column(String(60), nullable=True)
    step_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    progress: Mapped[float | None] = mapped_column(Float, nullable=True)

    processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    succeeded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    warnings: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    cancel_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        onupdate=lambda: datetime.now(datetime.now().astimezone().tzinfo),
    )

    __table_args__ = (
        Index("ix_operation_jobs_owner_status", "created_by", "status"),
        Index("ix_operation_jobs_owner_created", "created_by", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover - depuração
        return f"<OperationJob(id={self.id}, kind={self.kind}, status={self.status})>"
