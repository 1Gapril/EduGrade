"""Schemas comuns: Paginação, Filtros, Respostas padronizadas."""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ==================== Pagination ====================

class PaginationParams(BaseModel):
    """Parâmetros de paginação."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica."""
    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate(
    items: list[T],
    total: int,
    params: PaginationParams,
) -> PaginatedResponse[T]:
    """Cria resposta paginada."""
    total_pages = (total + params.page_size - 1) // params.page_size
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1,
    )


# ==================== Filter Base ====================

class FilterParams(BaseModel):
    """Parâmetros base de filtro."""
    search: str | None = None
    order_by: str | None = None
    order_desc: bool = False


class DateRangeFilter(BaseModel):
    """Filtro por intervalo de datas."""
    start_date: datetime | None = None
    end_date: datetime | None = None


# ==================== Standard Responses ====================

class MessageResponse(BaseModel):
    """Resposta simples de mensagem."""
    message: str
    detail: str | None = None


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""
    error: str
    message: str
    detail: str | None = None
    code: str | None = None


class ValidationErrorDetail(BaseModel):
    """Detalhe de erro de validação."""
    field: str
    message: str
    value: Any = None


class ValidationErrorResponse(ErrorResponse):
    """Resposta de erro de validação."""
    errors: list[ValidationErrorDetail]


class SuccessResponse(BaseModel, Generic[T]):
    """Resposta de sucesso com dados."""
    success: bool = True
    data: T
    message: str | None = None


class CreatedResponse(BaseModel, Generic[T]):
    """Resposta de criação (201)."""
    success: bool = True
    data: T
    message: str = "Recurso criado com sucesso"


class DeletedResponse(BaseModel):
    """Resposta de exclusão (204)."""
    success: bool = True
    message: str = "Recurso removido com sucesso"


# ==================== ID Response ====================

class IDResponse(BaseModel):
    """Resposta com ID do recurso criado."""
    id: UUID
    message: str = "Recurso criado com sucesso"


# ==================== Bulk Operations ====================

class BulkOperationRequest(BaseModel, Generic[T]):
    """Requisição de operação em lote."""
    items: list[T]


class BulkOperationResult(BaseModel):
    """Resultado de operação em lote."""
    success_count: int
    failure_count: int
    errors: list[dict] = Field(default_factory=list)
    successful_ids: list[UUID] = Field(default_factory=list)


# ==================== Health Check ====================

class HealthCheckResponse(BaseModel):
    """Health check da aplicação."""
    status: str
    version: str
    timestamp: datetime
    database: str
    services: dict = Field(default_factory=dict)


class ServiceStatus(BaseModel):
    """Status de um serviço."""
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: int | None = None
    error: str | None = None


# ==================== File Upload ====================

class FileUploadResponse(BaseModel):
    """Resposta de upload de arquivo."""
    filename: str
    content_type: str
    size: int
    path: str
    url: str | None = None


class FileUploadRequest(BaseModel):
    """Requisição de upload (metadata)."""
    filename: str
    content_type: str
    size: int


# ==================== Export/Import ====================

class ExportRequest(BaseModel):
    """Requisição de exportação."""
    format: str = Field(default="json", pattern="^(json|csv|xlsx|pdf)$")
    filters: dict | None = None
    fields: list[str] | None = None


class ImportRequest(BaseModel):
    """Requisição de importação."""
    file_path: str
    format: str = Field(default="json", pattern="^(json|csv|xlsx)$")
    options: dict | None = None


class ImportResult(BaseModel):
    """Resultado de importação."""
    imported: int
    failed: int
    errors: list[dict] = Field(default_factory=list)
