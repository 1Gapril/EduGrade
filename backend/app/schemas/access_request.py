"""Schemas para solicitações de acesso."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from backend.app.models.access_request import AccessRequestStatus


class AccessRequestCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    phone: str | None = Field(default=None, max_length=40)
    requested_role: str = Field(pattern="^(student|teacher|admin)$")
    justification: str = Field(min_length=10, max_length=2000)


class AccessRequestAccountCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    role: str = Field(pattern="^(student|teacher|admin)$")


class AccessRequestResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    username: str
    phone: str | None
    requested_role: str
    justification: str
    status: AccessRequestStatus
    account_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
