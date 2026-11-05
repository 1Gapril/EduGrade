"""API Routes para Processamento em Lote (Batch Grading)."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.api.routes.exams import (
    _assert_exam_access,
    _assert_version_access,
    _teacher_class_ids,
)
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.integrations.storage import FileStorage
from backend.app.models.exam import Exam
from backend.app.models.grading_batch import (
    BatchStatus,
    FileStatus,
    GradingAuditLog,
    GradingBatch,
    StudentIdentificationResult,
)
from backend.app.models.user import User, UserRole
from backend.app.schemas.grading_batch import (
    BatchProgressResponse,
    GradingBatchCreate,
    GradingBatchDetail,
    GradingBatchFileResponse,
    GradingBatchList,
    GradingBatchResponse,
    PendingIdentificationsResponse,
    StudentIdentificationResultResponse,
    StudentIdentificationUpdate,
)
from backend.app.services.batch_grading_service import BatchGradingService

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


def _assert_batch_access(
    db: Session,
    current_user: User,
    batch_id: UUID,
    permission: str = "receive_submissions",
) -> GradingBatch:
    batch = db.get(GradingBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    exam = _assert_exam_access(db, current_user, batch.exam_id, permission)
    if exam.id != batch.exam_id:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return batch


# ==================== Batch Management ====================

@router.post("/", response_model=GradingBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_data: GradingBatchCreate,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Cria novo lote de processamento."""
    _assert_exam_access(service.db, current_user, batch_data.exam_id, "upload_submissions")
    version = _assert_version_access(
        service.db, current_user, batch_data.version_id, "upload_submissions"
    )
    if version.exam_id != batch_data.exam_id:
        raise HTTPException(status_code=422, detail="A versão não pertence à prova informada")
    batch = service.create_batch(
        exam_id=batch_data.exam_id,
        version_id=batch_data.version_id,
        uploaded_by=current_user.id,
    )
    return batch


@router.get("/", response_model=GradingBatchList)
async def list_batches(
    exam_id: UUID | None = Query(None, description="Filtrar por prova"),
    status_filter: BatchStatus | None = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Lista lotes com paginação e filtros."""
    query = service.db.query(GradingBatch)
    if current_user.role == UserRole.TEACHER:
        allowed_classes = (
            _teacher_class_ids(service.db, current_user, "receive_submissions")
            | _teacher_class_ids(service.db, current_user, "upload_submissions")
        )
        query = query.join(Exam, GradingBatch.exam_id == Exam.id).filter(
            Exam.class_id.in_(allowed_classes) if allowed_classes else False
        )
    if exam_id is not None:
        query = query.filter(GradingBatch.exam_id == exam_id)
    if status_filter is not None:
        query = query.filter(GradingBatch.status == status_filter)
    total = query.count()
    items = query.order_by(GradingBatch.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return GradingBatchList(
        items=items,
        total=total,
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
    _assert_batch_access(service.db, current_user, batch_id)
    details = service.get_batch_with_details(batch_id)
    return details


@router.post("/{batch_id}/files", response_model=list[GradingBatchFileResponse])
async def add_files(
    batch_id: UUID,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Adiciona arquivos ao lote (upload multipart)."""
    batch = _assert_batch_access(service.db, current_user, batch_id, "upload_submissions")
    if batch.status != BatchStatus.UPLOADING:
        raise HTTPException(status_code=409, detail="Lote não está em estado de upload")
    if not files:
        raise HTTPException(status_code=422, detail="Envie ao menos um arquivo")
    if len(files) > 100:
        raise HTTPException(status_code=422, detail="Envie no máximo 100 arquivos por requisição")

    storage = FileStorage()
    file_records = []
    saved_paths = []
    for upload in files:
        filename = upload.filename or "arquivo-sem-nome"
        suffix = Path(filename.replace("\\", "/")).suffix.lower()
        file_type = "pdf" if suffix == ".pdf" else "image"
        stored_path = None
        try:
            stored_path = await storage.save(upload, folder="exams")
            file_size = Path(stored_path).stat().st_size
            saved_paths.append(stored_path)
        except HTTPException as exc:
            failure_message = str(exc.detail)
            stored_path = None
        except OSError:
            if stored_path is not None:
                Path(stored_path).unlink(missing_ok=True)
                stored_path = None
            failure_message = "Não foi possível armazenar o arquivo."
        finally:
            await upload.close()
        file_records.append({
            "filename": filename,
            "path": stored_path or "",
            "content_type": upload.content_type or "application/octet-stream",
            "size": file_size if stored_path is not None else 0,
            "type": file_type,
            "page_count": 1,
            "status": FileStatus.PENDING if stored_path is not None else FileStatus.FAILED,
            "error_message": failure_message if stored_path is None else None,
        })

    try:
        records = service.add_files(batch_id, file_records, uploaded_by=current_user.id)
        service.db.commit()
        return records
    except Exception:
        service.db.rollback()
        for saved_path in saved_paths:
            Path(saved_path).unlink(missing_ok=True)
        raise


@router.post("/{batch_id}/start", response_model=GradingBatchResponse)
async def start_processing(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Inicia processamento assíncrono do lote."""
    _assert_batch_access(service.db, current_user, batch_id)
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
    _assert_batch_access(service.db, current_user, batch_id, "run_ocr")
    batch = service.process_batch_files(batch_id)
    return batch


@router.post("/{batch_id}/identify", response_model=GradingBatchResponse)
async def identify_students(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Identifica alunos em todas as páginas usando IA/OCR."""
    _assert_batch_access(service.db, current_user, batch_id, "receive_submissions")
    batch = service.identify_students(batch_id)
    return batch


@router.post("/{batch_id}/group", response_model=GradingBatchResponse)
async def group_pages(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Agrupa páginas por aluno/prova."""
    _assert_batch_access(service.db, current_user, batch_id, "receive_submissions")
    batch = service.group_pages(batch_id)
    return batch


@router.post("/{batch_id}/create-submissions", response_model=GradingBatchResponse)
async def create_submissions(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Cria submissões a partir dos grupos de páginas."""
    _assert_batch_access(service.db, current_user, batch_id, "receive_submissions")
    service.create_submissions_from_groups(batch_id)
    batch = service.get_batch(batch_id)
    return batch


@router.post("/{batch_id}/grade", response_model=GradingBatchResponse)
async def grade_all(
    batch_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    service: BatchGradingService = Depends(get_batch_service),
):
    """Executa correção por IA em todas as submissões."""
    _assert_batch_access(service.db, current_user, batch_id, "grade_questions")
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
    _assert_batch_access(service.db, current_user, batch_id)
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
    ident = service.db.get(StudentIdentificationResult, identification_id)
    if ident is None:
        raise HTTPException(status_code=404, detail="Identificação não encontrada")
    page = service.db.get(service.page_repo, ident.page_id)
    if page is None:
        raise HTTPException(status_code=404, detail="Página da prova não encontrada")
    batch_file = service.db.get(service.file_repo, page.batch_file_id)
    if batch_file is None:
        raise HTTPException(status_code=404, detail="Arquivo do lote não encontrado")
    _assert_batch_access(service.db, current_user, batch_file.batch_id)
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
    _assert_batch_access(service.db, current_user, batch_id)
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

@router.get("/{batch_id}/audit", response_model=list[dict])
async def get_audit_logs(
    batch_id: UUID,
    action: str | None = Query(None, description="Filtrar por ação"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Obtém logs de auditoria do lote."""
    _assert_batch_access(db, current_user, batch_id, "view_history")
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
