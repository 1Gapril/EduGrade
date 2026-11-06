"""Response schemas for audit events."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.app.models.audit import AuditActionType


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    action: AuditActionType
    entity_type: str | None
    entity_id: UUID | None
    description: str
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    session_id: str | None
    success: bool
    error_message: str | None
    created_at: datetime
