"""API Routes para Processamento em Lote (Batch Grading) - ADENDO OFICIAL."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User, UserRole
from backend.app.models.grading_batch import (
    GradingBatch, BatchStatus, GradingBatchFile, FileStatus,
    ExamSubmissionPage, StudentIdentificationResult, IdentificationStatus,
    ExamPageGroup, PageGroupStatus, GradingAuditLog,
)
from backend.app.schemas.grading_batch import (
    GradingBatchCreate, GradingBatchResponse, GradingBatchDetail,
    GradingBatchFileResponse, GradingBatchList,
    StudentIdentificationResultResponse, StudentIdentificationUpdate,
    ExamPageGroupResponse, BatchProcessingStart,
    PendingIdentificationsResponse, BatchProgressResponse,
)
from backend.app.services.batch_grading_service import BatchGradingService
from backend.app.core.exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/batch-grading", tags=["Processamento em Lote"])


def get_batch_service(db: Session = Depends(get_db)) -> BatchGradingService:
    """Dependency para obter o serviço de batch grading."""
    return BatchGradingService(db)


def require_teacher_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verifica se o usuário é professor ou admin."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a professores e administradores"
        )
    return current_user


# ==================== Batch Management ====================

@router.post("/", response_model=GradingBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_data: GradingBatchCreate,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Cria novo lote de processamento."""
    batch = service.create_batch(
        exam_id=batch_data.exam_id,
        version_id=batch_data.version_id,
        uploaded_by=current_user.id,
    )
    return batch


@router.get("/", response_model=GradingBatchList)
async def list_batches(
    exam_id: Optional[UUID] = Query(None, description="Filtrar por prova"),
    status_filter: Optional[BatchStatus] = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Lista lotes com paginação e filtros."""
    # TODO: Implementar listagem com filtros
    # Por enquanto retorna vazio
    return GradingBatchList(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.get("/{batch_id}", response_model=GradingBatchDetail)
async def get_batch(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Obtém detalhes completos do lote."""
    details = service.get_batch_with_details(batch_id)
    return details


@router.post("/{batch_id}/files", response_model=List[GradingBatchFileResponse])
async def add_files(
    batch_id: UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Adiciona arquivos ao lote (upload multipart)."""
    # TODO: Implementar upload de arquivos
    # Salva arquivos em storage e cria registros
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Upload de arquivos não implementado ainda"
    )


@router.post("/{batch_id}/start", response_model=GradingBatchResponse)
async def start_processing(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Inicia processamento assíncrono do lote."""
    batch = service.start_processing(batch_id)
    return batch


# ==================== Processing Steps ====================

@router.post("/{batch_id}/process-pages", response_model=GradingBatchResponse)
async def process_batch_pages(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Processa todos os arquivos do lote (páginas, OCR, etc.)."""
    batch = service.process_batch_files(batch_id)
    return batch


@router.post("/{batch_id}/identify", response_model=GradingBatchResponse)
async def identify_students(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Identifica alunos em todas as páginas usando IA/OCR."""
    batch = service.identify_students(batch_id)
    return batch


@router.post("/{batch_id}/group", response_model=GradingBatchResponse)
async def group_pages(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Agrupa páginas por aluno/prova."""
    batch = service.group_pages(batch_id)
    return batch


@router.post("/{batch_id}/create-submissions", response_model=GradingBatchResponse)
async def create_submissions(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Cria submissões a partir dos grupos de páginas."""
    submissions = service.create_submissions_from_groups(batch_id)
    batch = service.get_batch(batch_id)
    return batch


@router.post("/{batch_id}/grade", response_model=GradingBatchResponse)
async def grade_all(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Executa correção por IA em todas as submissões."""
    batch = await service.grade_all_submissions(batch_id)
    return batch


# ==================== Manual Operations ====================

@router.get("/{batch_id}/pending-identifications", response_model=PendingIdentificationsResponse)
async def get_pending_identifications(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Busca identificações pendentes de revisão manual."""
    identifications = service.get_pending_identifications(batch_id)
    return PendingIdentificationsResponse(
        items=identifications,
        total=len(identifications),
    )


@router.put("/identifications/{identification_id}/manual", response_model=StudentIdentificationResultResponse)
async def manual_identify(
    identification_id: UUID,
    update_data: StudentIdentificationUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Identificação manual pelo professor."""
    result = service.manual_identify(
        identification_id=identification_id,
        student_id=update_data.student_id,
        teacher_id=current_user.id,
    )
    return result


# ==================== Progress Tracking ====================

@router.get("/{batch_id}/progress", response_model=BatchProgressResponse)
async def get_progress(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Obtém progresso detalhado do processamento."""
    batch = service.get_batch(batch_id)
    details = service.get_batch_with_details(batch_id)
    return BatchProgressResponse(
        batch_id=batch_id,
        status=batch.status,
        progress=details["progress"],
        file_stats=details["file_stats"],
        submission_stats=details["submission_stats"],
        pending_identifications=details["pending_identifications"],
    )


# ==================== Audit ====================

@router.get("/{batch_id}/audit", response_model=List[dict])
async def get_audit_logs(
    batch_id: UUID,
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Obtém logs de auditoria do lote."""
    query = db.query(GradingAuditLog).filter(GradingAuditLog.batch_id == batch_id)
    if action:
        query = query.filter(GradingAuditLog.action == action)
    logs = query.order_by(GradingAuditLog.created_at.desc()).limit(limit).all()

    return [
        {
            "id": str(log.id),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "description": log.description,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "performed_by": str(log.performed_by) if log.performed_by else None,
            "success": log.success,
            "error_message": log.error_message,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]