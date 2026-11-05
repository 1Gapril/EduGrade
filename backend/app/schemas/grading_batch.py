"""Schemas para Processamento em Lote (Batch Grading) - ADENDO OFICIAL."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ==================== Enums ====================

class BatchStatus(str, Enum):
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


class FileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"


class IdentificationStatus(str, Enum):
    IDENTIFIED = "identified"
    PENDING = "pending"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    MANUAL = "manual"


class PageGroupStatus(str, Enum):
    PENDING = "pending"
    GROUPED = "grouped"
    CONFLICT = "conflict"
    MANUAL_REVIEW = "manual_review"


# ==================== Batch Schemas ====================

class GradingBatchCreate(BaseModel):
    """Schema para criação de lote."""
    exam_id: UUID = Field(..., description="ID da prova")
    version_id: UUID = Field(..., description="ID da versão da prova")


class GradingBatchBase(BaseModel):
    """Campos base do lote."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exam_id: UUID
    version_id: UUID
    uploaded_by: UUID
    status: BatchStatus
    total_files: int
    processed_files: int
    total_pages: int
    identified_students: int
    grouped_submissions: int
    graded_submissions: int
    pending_review: int
    failed_files: int
    error_message: str | None
    processing_started_at: datetime | None
    processing_completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class GradingBatchResponse(GradingBatchBase):
    """Schema de resposta do lote."""
    pass


class GradingBatchDetail(GradingBatchBase):
    """Schema de detalhes do lote (para painel)."""
    file_stats: dict[str, int] = Field(default_factory=dict)
    submission_stats: dict[str, int] = Field(default_factory=dict)
    pending_identifications: int = 0
    progress: dict[str, Any] = Field(default_factory=dict)


class GradingBatchList(BaseModel):
    """Lista paginada de lotes."""
    items: list[GradingBatchResponse]
    total: int
    page: int
    page_size: int


# ==================== File Schemas ====================

class GradingBatchFileBase(BaseModel):
    """Campos base do arquivo."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    batch_id: UUID
    original_filename: str
    stored_path: str
    content_type: str
    file_size: int
    file_type: str
    page_count: int
    status: FileStatus
    processed_pages: int
    error_message: str | None
    created_at: datetime
    processed_at: datetime | None


class GradingBatchFileResponse(GradingBatchFileBase):
    """Schema de resposta do arquivo."""
    pass


# ==================== Page Schemas ====================

class ExamSubmissionPageBase(BaseModel):
    """Campos base da página."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    batch_file_id: UUID
    submission_id: UUID | None
    page_number: int
    original_image_path: str
    processed_image_path: str | None
    rotation_angle: float
    perspective_corrected: bool
    ocr_confidence: Decimal | None
    full_text: str | None
    created_at: datetime


class ExamSubmissionPageResponse(ExamSubmissionPageBase):
    """Schema de resposta da página."""
    pass


# ==================== Identification Schemas ====================

class StudentIdentificationResultBase(BaseModel):
    """Campos base do resultado de identificação."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    page_id: UUID
    submission_id: UUID | None
    identified_ra: str | None
    identified_matricula: str | None
    identified_name: str | None
    identified_exam_code: str | None
    identified_class_code: str | None
    identified_copy_code: str | None
    matched_student_id: UUID | None
    ra_confidence: Decimal | None
    matricula_confidence: Decimal | None
    match_type: str
    status: IdentificationStatus
    conflict_details: dict[str, Any]
    manual_override: bool
    overridden_by: UUID | None
    overridden_at: datetime | None
    ai_provider: str
    ai_model: str
    created_at: datetime


class StudentIdentificationResultResponse(StudentIdentificationResultBase):
    """Schema de resposta da identificação."""
    pass


class StudentIdentificationUpdate(BaseModel):
    """Schema para atualização manual de identificação."""
    student_id: UUID = Field(..., description="ID do aluno identificado manualmente")


class PendingIdentificationsResponse(BaseModel):
    """Resposta para identificações pendentes."""
    items: list[StudentIdentificationResultResponse]
    total: int


# ==================== Page Group Schemas ====================

class ExamPageGroupBase(BaseModel):
    """Campos base do agrupamento de páginas."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    batch_id: UUID
    student_id: UUID | None
    exam_id: UUID
    version_id: UUID
    copy_identifier: str | None
    page_ids: list[str]
    status: PageGroupStatus
    confidence: Decimal | None
    conflict_details: dict[str, Any]
    created_submission_id: UUID | None
    created_at: datetime


class ExamPageGroupResponse(ExamPageGroupBase):
    """Schema de resposta do agrupamento."""
    pass


# ==================== Processing Schemas ====================

class BatchProcessingStart(BaseModel):
    """Schema para iniciar processamento."""
    steps: list[str] | None = Field(
        default=None,
        description="Etapas a executar: process_pages, identify, group, create_submissions, grade"
    )


class BatchProgressResponse(BaseModel):
    """Resposta de progresso do lote."""
    batch_id: UUID
    status: BatchStatus
    progress: dict[str, Any]
    file_stats: dict[str, int]
    submission_stats: dict[str, int]
    pending_identifications: int
