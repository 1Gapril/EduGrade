"""Schemas Pydantic para Correção por IA e Revisão."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ==================== AI Correction Schemas ====================

class AICorrectionBase(BaseModel):
    """Campos base da correção por IA."""
    submission_id: UUID
    question_id: UUID
    extracted_answer_id: UUID | None = None
    provider: str
    model: str


class AICorrectionCreate(AICorrectionBase):
    """Schema para criação de correção por IA."""
    pass


class AICorrectionUpdate(BaseModel):
    """Schema para atualização de correção por IA."""
    status: str | None = None
    recognized_text: str | None = None
    interpretation: str | None = None
    suggested_score: Decimal | None = Field(None, ge=0)
    justification: str | None = None
    criteria_met: list[str] | None = None
    criteria_not_met: list[str] | None = None
    conceptual_errors: list[str] | None = None
    ocr_confidence: Decimal | None = Field(None, ge=0, le=100)
    evaluation_confidence: Decimal | None = Field(None, ge=0, le=100)
    requires_review: bool | None = None
    review_reason: str | None = None
    raw_response: dict[str, Any] | None = None
    prompt_used: str | None = None
    processing_time_ms: int | None = None
    error_message: str | None = None


class AICorrectionResponse(AICorrectionBase):
    """Schema de resposta da correção por IA."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    recognized_text: str | None = None
    interpretation: str | None = None
    suggested_score: Decimal | None = None
    max_score: Decimal
    justification: str | None = None
    criteria_met: list[str]
    criteria_not_met: list[str]
    conceptual_errors: list[str]
    ocr_confidence: Decimal | None = None
    evaluation_confidence: Decimal | None = None
    requires_review: bool
    review_reason: str | None = None
    raw_response: dict[str, Any]
    prompt_used: str | None = None
    processing_time_ms: int | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class AICorrectionWithReview(AICorrectionResponse):
    """Correção por IA com revisão."""
    review: Optional["CorrectionReviewResponse"] = None


# ==================== Correction Review Schemas ====================

class CorrectionReviewBase(BaseModel):
    """Campos base da revisão."""
    ai_correction_id: UUID
    reviewed_by: UUID


class CorrectionReviewCreate(CorrectionReviewBase):
    """Schema para criação de revisão."""
    pass


class CorrectionReviewUpdate(BaseModel):
    """Schema para atualização de revisão."""
    status: str | None = None
    final_score: Decimal | None = Field(None, ge=0)
    corrected_text: str | None = None
    reviewer_justification: str | None = None
    reviewer_notes: str | None = None
    criteria_overrides: dict[str, Any] | None = None


class CorrectionReviewResponse(CorrectionReviewBase):
    """Schema de resposta da revisão."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    original_suggested_score: Decimal | None = None
    final_score: Decimal | None = None
    corrected_text: str | None = None
    reviewer_justification: str | None = None
    reviewer_notes: str | None = None
    criteria_overrides: dict[str, Any]
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class CorrectionReviewWithAudit(CorrectionReviewResponse):
    """Revisão com logs de auditoria."""
    audit_logs: list["CorrectionAuditLogResponse"] = []


# ==================== Correction Audit Log Schemas ====================

class CorrectionAuditLogBase(BaseModel):
    """Campos base do log de auditoria da correção."""
    review_id: UUID
    action: str
    field_changed: str
    old_value: str | None = None
    new_value: str | None = None
    changed_by: UUID


class CorrectionAuditLogCreate(CorrectionAuditLogBase):
    """Schema para criação de log."""
    pass


class CorrectionAuditLogResponse(CorrectionAuditLogBase):
    """Schema de resposta do log."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    changed_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None


# ==================== AI Provider Schemas ====================

class AIProviderConfig(BaseModel):
    """Configuração do provedor de IA."""
    provider: str = Field(..., pattern="^(mock|ollama|openai|anthropic)$")
    model: str
    base_url: str | None = None
    api_key: str | None = None
    timeout_seconds: int = Field(default=120, ge=10, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)


class AIHealthCheck(BaseModel):
    """Health check do provedor de IA."""
    provider: str
    status: str
    model: str
    latency_ms: int | None = None
    error: str | None = None


class AIModelsList(BaseModel):
    """Lista de modelos disponíveis."""
    provider: str
    models: list[str]


# ==================== Correction Request/Response ====================

class CorrectionRequest(BaseModel):
    """Requisição de correção para o provedor de IA."""
    question_statement: str
    answer_key: dict[str, Any]
    rubric: dict[str, Any] | None = None
    max_score: Decimal
    student_answer: str
    student_answer_image: str | None = None  # base64
    question_type: str


class CorrectionResponse(BaseModel):
    """Resposta da correção do provedor de IA."""
    recognized_text: str
    interpretation: str
    suggested_score: Decimal
    max_score: Decimal
    justification: str
    criteria_met: list[str]
    criteria_not_met: list[str]
    conceptual_errors: list[str]
    ocr_confidence: Decimal | None = None
    evaluation_confidence: Decimal
    requires_review: bool
    review_reason: str | None = None
    raw_response: dict[str, Any]
    processing_time_ms: int


# ==================== Batch Correction ====================

class BatchCorrectionRequest(BaseModel):
    """Requisição de correção em lote."""
    submission_id: UUID
    question_ids: list[UUID] | None = None  # None = todas
    provider: str | None = None
    model: str | None = None


class BatchCorrectionResponse(BaseModel):
    """Resposta de correção em lote."""
    submission_id: UUID
    corrections: list[AICorrectionResponse]
    total_processed: int
    failed: int
    requires_review_count: int
    skipped: int = 0


# Forward references
CorrectionReviewWithAudit.model_rebuild()
