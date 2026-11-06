"""Service de Auditoria e Logs."""

from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.models.audit import AuditActionType, AuditLog, SystemLog
from backend.app.repositories.ai_correction_repository import (
    AuditLogRepository,
    SystemLogRepository,
)
from backend.app.schemas.common import PaginationParams, paginate


class AuditService:
    """Serviço de auditoria."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditLogRepository(db)
        self.system_repo = SystemLogRepository(db)

    def log_action(
        self,
        action: AuditActionType,
        description: str,
        user_id: UUID | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str | None = None,
        session_id: str | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditLog:
        """Registra ação de auditoria."""
        return self.repo.log(
            action=action,
            description=description,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            session_id=session_id,
            success=success,
            error_message=error_message,
        )

    def get_user_audit(self, user_id: UUID, params: PaginationParams) -> dict:
        """Busca auditoria de um usuário com paginação."""
        logs = self.repo.get_by_user(user_id, limit=params.limit)
        total = len(logs)  # Simplificado
        return paginate(logs, total, params)

    def get_entity_audit(self, entity_type: str, entity_id: UUID, params: PaginationParams) -> dict:
        """Busca auditoria de uma entidade."""
        logs = self.repo.get_by_entity(entity_type, entity_id)
        total = len(logs)
        return paginate(logs, total, params)

    def get_recent_audit(self, hours: int = 24, params: PaginationParams = None) -> dict:
        """Busca auditoria recente."""
        if params is None:
            params = PaginationParams()
        logs = self.repo.get_recent(hours=hours, limit=params.limit)
        total = len(logs)
        return paginate(logs, total, params)

    def get_action_audit(self, action: AuditActionType, params: PaginationParams) -> dict:
        """Busca auditoria por tipo de ação."""
        logs = self.repo.get_by_action(action, limit=params.limit)
        total = len(logs)
        return paginate(logs, total, params)


class SystemLogService:
    """Serviço de logs do sistema."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = SystemLogRepository(db)

    def log(
        self,
        level: str,
        logger: str,
        message: str,
        module: str | None = None,
        function: str | None = None,
        line_number: int | None = None,
        traceback: str | None = None,
        context: dict | None = None,
        user_id: UUID | None = None,
        request_id: str | None = None,
    ) -> SystemLog:
        """Registra log do sistema."""
        return self.repo.log(
            level=level,
            logger=logger,
            message=message,
            module=module,
            function=function,
            line_number=line_number,
            traceback=traceback,
            context=context,
            user_id=user_id,
            request_id=request_id,
        )

    def get_errors(self, hours: int = 24, limit: int = 100) -> list[SystemLog]:
        """Busca logs de erro recentes."""
        return self.repo.get_errors(hours=hours, limit=limit)
