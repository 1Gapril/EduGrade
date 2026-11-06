"""Schemas das operações de longa duração (barra global de progresso)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OperationStep(BaseModel):
    """Etapa executada dentro de uma operação."""

    key: str
    label: str
    started_at: datetime | None = None
    finished_at: datetime | None = None


class OperationJobResponse(BaseModel):
    """Estado atual (snapshot) de uma operação."""

    id: UUID
    kind: str
    title: str
    status: str
    step_key: str | None = None
    step_label: str | None = None
    progress: float | None = Field(
        default=None,
        description="Percentual real (0-100) ou null quando indeterminado.",
    )
    processed: int
    total: int
    succeeded: int
    failed: int
    skipped: int
    message: str | None = None
    error: str | None = None
    warnings: list[str] = Field(default_factory=list)
    payload: dict = Field(default_factory=dict)
    result: dict | None = None
    cancel_requested: bool
    can_cancel: bool
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    elapsed_seconds: float


class OperationJobListResponse(BaseModel):
    """Lista de operações do usuário autenticado."""

    items: list[OperationJobResponse]
    total: int


class OperationJobCreatedResponse(BaseModel):
    """Resposta ao iniciar uma operação em segundo plano."""

    job_id: UUID
    status: str
    message: str = "Operação iniciada. Acompanhe o progresso pelo painel."


class SubmissionUploadResponse(BaseModel):
    """Arquivo recebido individualmente, antes de compor a submissão."""

    path: str
    filename: str
    size_bytes: int


class SubmissionFromUploadsRequest(BaseModel):
    """Compõe a submissão a partir dos arquivos já enviados."""

    copy_id: UUID
    uploads: list[SubmissionUploadResponse] = Field(min_length=1)
    student_id: UUID | None = None
