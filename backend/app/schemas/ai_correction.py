"""Schemas Pydantic para Correção por IA e Revisão."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# ==================== AI Correction Schemas ====================

class AICorrectionBase(BaseModel):
    """Campos base da correção por IA."""
    submission_id: UUID
    question_id: UUID
    extracted_answer_id: Optional[UUID] = None
    provider: str
    model: str


class AICorrectionCreate(AICorrectionBase):
    """Schema para criação de correção por IA."""
    pass


class AICorrectionUpdate(BaseModel):
    """Schema para atualização de correção por IA."""
    status: Optional[str] = None
    recognized_text: Optional[str] = None
    interpretation: Optional[str] = None
    suggested_score: Optional[Decimal] = Field(None, ge=0)
    justification: Optional[str] = None
    criteria_met: Optional[List[str]] = None
    criteria_not_met: Optional[List[str]] = None
    conceptual_errors: Optional[List[str]] = None
    ocr_confidence: Optional[Decimal] = Field(None, ge=0, le=100)
    evaluation_confidence: Optional[Decimal] = Field(None, ge=0, le=100)
    requires_review: Optional[bool] = None
    review_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    prompt_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None


class AICorrectionResponse(AICorrectionBase):
    """Schema de resposta da correção por IA."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    recognized_text: Optional[str] = None
    interpretation: Optional[str] = None
    suggested_score: Optional[Decimal] = None
    max_score: Decimal
    justification: Optional[str] = None
    criteria_met: List[str]
    criteria_not_met: List[str]
    conceptual_errors: List[str]
    ocr_confidence: Optional[Decimal] = None
    evaluation_confidence: Optional[Decimal] = None
    requires_review: bool
    review_reason: Optional[str] = None
    raw_response: Dict[str, Any]
    prompt_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


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
    status: Optional[str] = None
    final_score: Optional[Decimal] = Field(None, ge=0)
    corrected_text: Optional[str] = None
    reviewer_justification: Optional[str] = None
    reviewer_notes: Optional[str] = None
    criteria_overrides: Optional[Dict[str, Any]] = None


class CorrectionReviewResponse(CorrectionReviewBase):
    """Schema de resposta da revisão."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    original_suggested_score: Optional[Decimal] = None
    final_score: Optional[Decimal] = None
    corrected_text: Optional[str] = None
    reviewer_justification: Optional[str] = None
    reviewer_notes: Optional[str] = None
    criteria_overrides: Dict[str, Any]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class CorrectionReviewWithAudit(CorrectionReviewResponse):
    """Revisão com logs de auditoria."""
    audit_logs: List["CorrectionAuditLogResponse"] = []


# ==================== Correction Audit Log Schemas ====================

class CorrectionAuditLogBase(BaseModel):
    """Campos base do log de auditoria da correção."""
    review_id: UUID
    action: str
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: UUID


class CorrectionAuditLogCreate(CorrectionAuditLogBase):
    """Schema para criação de log."""
    pass


class CorrectionAuditLogResponse(CorrectionAuditLogBase):
    """Schema de resposta do log."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    changed_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# ==================== AI Provider Schemas ====================

class AIProviderConfig(BaseModel):
    """Configuração do provedor de IA."""
    provider: str = Field(..., pattern="^(mock|ollama|openai|anthropic)$")
    model: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout_seconds: int = Field(default=120, ge=10, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)


class AIHealthCheck(BaseModel):
    """Health check do provedor de IA."""
    provider: str
    status: str
    model: str
    latency_ms: Optional[int] = None
    error: Optional[str] = None


class AIModelsList(BaseModel):
    """Lista de modelos disponíveis."""
    provider: str
    models: List[str]


# ==================== Correction Request/Response ====================

class CorrectionRequest(BaseModel):
    """Requisição de correção para o provedor de IA."""
    question_statement: str
    answer_key: Dict[str, Any]
    rubric: Optional[Dict[str, Any]] = None
    max_score: Decimal
    student_answer: str
    student_answer_image: Optional[str] = None  # base64
    question_type: str


class CorrectionResponse(BaseModel):
    """Resposta da correção do provedor de IA."""
    recognized_text: str
    interpretation: str
    suggested_score: Decimal
    max_score: Decimal
    justification: str
    criteria_met: List[str]
    criteria_not_met: List[str]
    conceptual_errors: List[str]
    ocr_confidence: Optional[Decimal] = None
    evaluation_confidence: Decimal
    requires_review: bool
    review_reason: Optional[str] = None
    raw_response: Dict[str, Any]
    processing_time_ms: int


# ==================== Batch Correction ====================

class BatchCorrectionRequest(BaseModel):
    """Requisição de correção em lote."""
    submission_id: UUID
    question_ids: Optional[List[UUID]] = None  # None = todas
    provider: Optional[str] = None
    model: Optional[str] = None


class BatchCorrectionResponse(BaseModel):
    """Resposta de correção em lote."""
    submission_id: UUID
    corrections: List[AICorrectionResponse]
    total_processed: int
    failed: int
    requires_review_count: int
    skipped: int = 0


# Forward references
CorrectionReviewWithAudit.model_rebuild()