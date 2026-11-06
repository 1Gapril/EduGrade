"""Rotas de Auditoria e Logs."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models.audit import AuditActionType
from backend.app.models.user import User
from backend.app.schemas.ai_correction import CorrectionAuditLogResponse
from backend.app.schemas.audit import AuditLogResponse
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.services.audit_service import AuditService, SystemLogService

router = APIRouter(prefix="/audit", tags=["Auditoria"])


# ==================== Audit Logs ====================

@router.get("", response_model=PaginatedResponse[AuditLogResponse])
def list_audit_logs(
    user_id: UUID | None = None,
    action: AuditActionType | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    hours: int = Query(default=24, ge=1, le=168),
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Lista logs de auditoria."""
    service = AuditService(db)

    if user_id:
        return service.get_user_audit(user_id, params)
    elif action:
        return service.get_action_audit(action, params)
    elif entity_type and entity_id:
        return service.get_entity_audit(entity_type, entity_id, params)
    else:
        return service.get_recent_audit(hours, params)


@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=PaginatedResponse[AuditLogResponse],
)
def get_entity_audit(
    entity_type: str,
    entity_id: UUID,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca auditoria de uma entidade específica."""
    service = AuditService(db)
    return service.get_entity_audit(entity_type, entity_id, params)


@router.get("/user/{user_id}", response_model=PaginatedResponse[AuditLogResponse])
def get_user_audit(
    user_id: UUID,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca auditoria de um usuário."""
    service = AuditService(db)
    return service.get_user_audit(user_id, params)


@router.get("/recent", response_model=PaginatedResponse[AuditLogResponse])
def get_recent_audit(
    hours: int = Query(default=24, ge=1, le=168),
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca auditoria recente."""
    service = AuditService(db)
    return service.get_recent_audit(hours, params)


# ==================== System Logs ====================

@router.get("/system/errors", response_model=list[dict])
def get_system_errors(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca logs de erro do sistema."""
    service = SystemLogService(db)
    logs = service.get_errors(hours=hours, limit=limit)
    return [
        {
            "id": str(log.id),
            "level": log.level,
            "logger": log.logger,
            "message": log.message,
            "module": log.module,
            "function": log.function,
            "traceback": log.traceback,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


# ==================== Correction Audit ====================

@router.get("/corrections/{review_id}/logs", response_model=list[CorrectionAuditLogResponse])
def get_correction_audit_logs(
    review_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca logs de auditoria de uma revisão de correção."""
    from backend.app.repositories.ai_correction_repository import CorrectionAuditLogRepository
    repo = CorrectionAuditLogRepository(db)
    return repo.get_by_review(review_id)
