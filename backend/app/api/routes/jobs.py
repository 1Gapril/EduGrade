"""Rotas de acompanhamento das operações de longa duração."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_active_user
from backend.app.models.user import User
from backend.app.schemas.operation_job import (
    OperationJobListResponse,
    OperationJobResponse,
)
from backend.app.services.operation_job_service import OperationJobService

router = APIRouter(prefix="/jobs", tags=["Operações"])


@router.get("", response_model=OperationJobListResponse)
def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Lista as operações recentes do usuário (para recuperar após recarregar)."""
    service = OperationJobService(db)
    jobs = service.list_recent(current_user, limit=limit)
    return OperationJobListResponse(
        items=[service.serialize(job) for job in jobs],
        total=len(jobs),
    )


@router.get("/{job_id}", response_model=OperationJobResponse)
def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Estado oficial do progresso da operação."""
    service = OperationJobService(db)
    job = service.get_for_user(job_id, current_user)
    return service.serialize(job)


@router.post("/{job_id}/cancel", response_model=OperationJobResponse)
def cancel_job(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Solicita o cancelamento cooperativo da operação."""
    service = OperationJobService(db)
    job = service.get_for_user(job_id, current_user)
    service.cancel(job.id)
    db.refresh(job)
    return service.serialize(job)
