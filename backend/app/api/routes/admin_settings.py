"""Administrator-only configuration and integration routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models.audit import AuditLog
from backend.app.models.user import User
from backend.app.schemas.admin_settings import (
    AdminSettingAuditResponse,
    AdminSettingsOverview,
    AIProviderConfigCreate,
    AIProviderConfigResponse,
    AIProviderConfigUpdate,
    FccNvidiaSyncRequest,
    FccSettingsUpdate,
    FccStatusResponse,
    ProviderTestResponse,
    SystemSettingsUpdate,
)
from backend.app.services.admin_settings_service import AdminSettingsService

router = APIRouter(prefix="/admin/settings", tags=["Configurações administrativas"])


@router.get("/overview", response_model=AdminSettingsOverview)
async def settings_overview(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AdminSettingsService(db)
    return service.overview(await service.fcc_status())


@router.get("/providers", response_model=list[AIProviderConfigResponse])
def list_providers(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return AdminSettingsService(db).list_providers()


@router.post(
    "/providers",
    response_model=AIProviderConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_provider(
    payload: AIProviderConfigCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        result = AdminSettingsService(db).create_provider(payload, current_user)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.put("/providers/{provider_id}", response_model=AIProviderConfigResponse)
def update_provider(
    provider_id: str,
    payload: AIProviderConfigUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        result = AdminSettingsService(db).update_provider(provider_id, payload, current_user)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(
    provider_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        AdminSettingsService(db).delete_provider(provider_id, current_user)
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.post(
    "/providers/{provider_id}/test",
    response_model=ProviderTestResponse,
)
async def test_provider(
    provider_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        result = await AdminSettingsService(db).test_provider(provider_id, current_user)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.get("/system")
def get_system_settings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return AdminSettingsService(db).get_runtime_settings()


@router.put("/system")
def update_system_settings(
    payload: SystemSettingsUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        result = AdminSettingsService(db).update_runtime_settings(
            payload.model_dump(exclude_unset=True), current_user
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.get("/fcc", response_model=FccStatusResponse)
async def get_fcc_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return await AdminSettingsService(db).fcc_status()


@router.put("/fcc", response_model=FccStatusResponse)
async def update_fcc_settings(
    payload: FccSettingsUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        service = AdminSettingsService(db)
        service.update_fcc_base_url(payload.base_url, current_user)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return await service.fcc_status()


@router.post("/fcc/test", response_model=FccStatusResponse)
async def test_fcc_connection(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return await AdminSettingsService(db).fcc_status()


@router.post("/fcc/sync/nvidia")
async def sync_nvidia_with_fcc(
    payload: FccNvidiaSyncRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        result = await AdminSettingsService(db).sync_nvidia_to_fcc(
            payload.model, current_user
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.get("/audit", response_model=list[AdminSettingAuditResponse])
def list_settings_audit(
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    safe_limit = max(1, min(limit, 200))
    return list(
        db.execute(
            select(AuditLog)
            .where(AuditLog.entity_type == "AdminSettings")
            .order_by(AuditLog.created_at.desc())
            .limit(safe_limit)
        ).scalars()
    )
