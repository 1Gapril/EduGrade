"""Modelos de Auditoria e Logs do Sistema."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from backend.app.models.user import User

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class AuditActionType(str, enum.Enum):
    """Tipos de ação auditadas."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    GRADE_PUBLISH = "grade_publish"
    GRADE_CHANGE = "grade_change"
    EXAM_CREATE = "exam_create"
    EXAM_PUBLISH = "exam_publish"
    EXAM_PRINT = "exam_print"
    EXAM_UPLOAD = "exam_upload"
    AI_CORRECTION_REQUEST = "ai_correction_request"
    AI_CORRECTION_REVIEW = "ai_correction_review"
    CONFIG_CHANGE = "config_change"
    BACKUP_CREATE = "backup_create"
    BACKUP_RESTORE = "backup_restore"


class AuditLog(Base):
    """Log de auditoria geral do sistema."""

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[AuditActionType] = mapped_column(
        Enum(AuditActionType, native_enum=False),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    entity_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    success: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
        index=True,
    )

    # Relacionamentos
    user: Mapped["User"] = relationship(lazy="selectin")

    __table_args__ = (
        Index("ix_audit_logs_user_created", "user_id", "created_at"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_action_created", "action", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


class SystemLog(Base):
    """Log de eventos do sistema (erros, warnings, info)."""

    __tablename__ = "system_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    module: Mapped[str | None] = mapped_column(String(255), nullable=True)
    function: Mapped[str | None] = mapped_column(String(255), nullable=True)
    line_number: Mapped[int | None] = mapped_column(nullable=True)
    traceback: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("ix_system_logs_level_created", "level", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SystemLog(id={self.id}, level={self.level}, logger={self.logger})>"
