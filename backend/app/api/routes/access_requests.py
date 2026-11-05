"""Rotas para solicitação pública e aprovação administrativa de acesso."""

import secrets
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.integrations.email import EmailDeliveryError, send_account_credentials
from backend.app.models.access_request import AccessRequest, AccessRequestStatus
from backend.app.models.user import User
from backend.app.schemas.access_request import (
    AccessRequestAccountCreate,
    AccessRequestCreate,
    AccessRequestResponse,
)
from backend.app.schemas.user import UserCreate
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/access-requests", tags=["Solicitações de acesso"])


@router.post("", response_model=AccessRequestResponse, status_code=status.HTTP_201_CREATED)
def create_access_request(
    request_data: AccessRequestCreate,
    db: Session = Depends(get_db),
):
    """Registra um pedido de acesso sem criar uma conta automaticamente."""
    email = str(request_data.email).strip().lower()
    existing_user = db.execute(
        select(User.id).where(func.lower(User.email) == email)
    ).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail")

    existing_request = db.execute(
        select(AccessRequest.id).where(
            func.lower(AccessRequest.email) == email,
            AccessRequest.status == AccessRequestStatus.OPEN,
        )
    ).scalar_one_or_none()
    if existing_request:
        raise HTTPException(status_code=409, detail="Já existe uma solicitação aberta para este e-mail")

    access_request = AccessRequest(
        full_name=request_data.full_name.strip(),
        email=email,
        username=request_data.username.strip(),
        phone=request_data.phone.strip() if request_data.phone else None,
        requested_role=request_data.requested_role,
        justification=request_data.justification.strip(),
    )
    db.add(access_request)
    try:
        db.commit()
        db.refresh(access_request)
    except Exception:
        db.rollback()
        raise
    return access_request


@router.get("/pending-count")
def count_pending_requests(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    count = db.execute(
        select(func.count(AccessRequest.id)).where(
            AccessRequest.status == AccessRequestStatus.OPEN
        )
    ).scalar_one()
    return {"count": count}


@router.get("", response_model=list[AccessRequestResponse])
def list_access_requests(
    request_status: AccessRequestStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    statement = select(AccessRequest).order_by(AccessRequest.created_at.desc())
    if request_status is not None:
        statement = statement.where(AccessRequest.status == request_status)
    return list(db.execute(statement).scalars().all())


@router.post("/{request_id}/create-account", response_model=AccessRequestResponse)
def create_account_from_request(
    request_id: UUID,
    account_data: AccessRequestAccountCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    access_request = db.get(AccessRequest, request_id)
    if not access_request:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if access_request.status != AccessRequestStatus.OPEN:
        raise HTTPException(status_code=409, detail="Esta solicitação já foi atendida")

    if not settings.smtp_host:
        raise HTTPException(
            status_code=503,
            detail="O envio de senha está indisponível: configure SMTP_HOST no servidor.",
        )

    temporary_password = secrets.token_urlsafe(18)
    user_data = UserCreate(
        full_name=access_request.full_name,
        email=access_request.email,
        username=account_data.username,
        role=account_data.role,
        password=temporary_password,
    )
    try:
        user = UserService(db).create_user(user_data, current_user.id)
        send_account_credentials(
            access_request.email,
            access_request.full_name,
            account_data.username,
            temporary_password,
        )
        access_request.status = AccessRequestStatus.APPROVED
        access_request.account_id = user.id
        access_request.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(access_request)
    except EmailDeliveryError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return access_request


@router.post("/{request_id}/reject", response_model=AccessRequestResponse)
def reject_access_request(
    request_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    access_request = db.get(AccessRequest, request_id)
    if not access_request:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if access_request.status != AccessRequestStatus.OPEN:
        raise HTTPException(status_code=409, detail="Esta solicitação já foi atendida")

    access_request.status = AccessRequestStatus.REJECTED
    access_request.updated_at = datetime.now(UTC)
    try:
        db.commit()
        db.refresh(access_request)
    except Exception:
        db.rollback()
        raise
    return access_request
