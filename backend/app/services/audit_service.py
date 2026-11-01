"""Service de Auditoria e Logs."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.app.models.audit import AuditLog, AuditActionType, SystemLog
from backend.app.repositories.ai_correction_repository import AuditLogRepository, SystemLogRepository
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
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
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
        module: Optional[str] = None,
        function: Optional[str] = None,
        line_number: Optional[int] = None,
        traceback: Optional[str] = None,
        context: Optional[dict] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
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

    def get_errors(self, hours: int = 24, limit: int = 100) -> List[SystemLog]:
        """Busca logs de erro recentes."""
        return self.repo.get_errors(hours=hours, limit=limit)