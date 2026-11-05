"""Modelos de Correção por IA e Revisão."""

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from backend.app.models.exam import ExamQuestion, ExamSubmission, ExtractedAnswer
    from backend.app.models.user import User

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
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


class AICorrectionStatus(str, enum.Enum):
    """Status da correção por IA."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    LOW_CONFIDENCE = "low_confidence"
    REQUIRES_REVIEW = "requires_review"


class ReviewStatus(str, enum.Enum):
    """Status da revisão do professor."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    MODIFIED = "modified"
    REJECTED = "rejected"


class AICorrection(Base):
    """Correção sugerida pela IA para uma questão."""

    __tablename__ = "ai_corrections"

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
    question_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    extracted_answer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("extracted_answers.id", ondelete="SET NULL"),
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[AICorrectionStatus] = mapped_column(
        Enum(AICorrectionStatus, native_enum=False),
        default=AICorrectionStatus.PENDING,
        nullable=False,
    )
    recognized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_score: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=False,
    )
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_met: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    criteria_not_met: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    conceptual_errors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    ocr_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    evaluation_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    prompt_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    submission: Mapped["ExamSubmission"] = relationship("ExamSubmission", back_populates="ai_corrections", lazy="selectin")
    question: Mapped["ExamQuestion"] = relationship(lazy="selectin")
    extracted_answer: Mapped["ExtractedAnswer"] = relationship(lazy="selectin")
    reviews: Mapped[list["CorrectionReview"]] = relationship(
        "CorrectionReview",
        back_populates="ai_correction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("suggested_score IS NULL OR (suggested_score >= 0 AND suggested_score <= max_score)", name="ck_ai_score_valid"),
        CheckConstraint("ocr_confidence IS NULL OR (ocr_confidence >= 0 AND ocr_confidence <= 100)", name="ck_ai_ocr_confidence"),
        CheckConstraint("evaluation_confidence IS NULL OR (evaluation_confidence >= 0 AND evaluation_confidence <= 100)", name="ck_ai_eval_confidence"),
        Index("ix_ai_corrections_submission_question", "submission_id", "question_id"),
    )

    def __repr__(self) -> str:
        return f"<AICorrection(id={self.id}, question_id={self.question_id}, status={self.status})>"


class CorrectionReview(Base):
    """Revisão da correção pelo professor."""

    __tablename__ = "correction_reviews"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    ai_correction_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ai_corrections.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    reviewed_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        default=ReviewStatus.PENDING,
        nullable=False,
    )
    original_suggested_score: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    final_score: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_overrides: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )

    # Relacionamentos
    ai_correction: Mapped[AICorrection] = relationship("AICorrection", back_populates="reviews", lazy="selectin")
    reviewer: Mapped["User"] = relationship(lazy="selectin")
    audit_logs: Mapped[list["CorrectionAuditLog"]] = relationship(
        "CorrectionAuditLog",
        back_populates="review",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("final_score IS NULL OR final_score >= 0", name="ck_review_final_score_valid"),
    )

    def __repr__(self) -> str:
        return f"<CorrectionReview(id={self.id}, ai_correction_id={self.ai_correction_id}, status={self.status})>"


class CorrectionAuditLog(Base):
    """Log de auditoria das alterações na correção."""

    __tablename__ = "correction_audit_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    review_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("correction_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # score_change, text_correction, criteria_override, etc.
    field_changed: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relacionamentos
    review: Mapped[CorrectionReview] = relationship("CorrectionReview", back_populates="audit_logs", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CorrectionAuditLog(id={self.id}, review_id={self.review_id}, action={self.action})>"
