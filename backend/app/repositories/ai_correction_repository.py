"""Repository de Correção por IA e Auditoria."""

from datetime import UTC
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.ai_correction import (
    AICorrection,
    AICorrectionStatus,
    CorrectionAuditLog,
    CorrectionReview,
    ReviewStatus,
)
from backend.app.models.audit import AuditActionType, AuditLog, SystemLog
from backend.app.repositories.base import BaseRepository


class AICorrectionRepository(BaseRepository[AICorrection]):
    """Repository para correções por IA."""

    def __init__(self, db: Session):
        super().__init__(AICorrection, db)

    def get_by_submission(self, submission_id: UUID) -> list[AICorrection]:
        """Busca correções de uma submissão."""
        return self.get_all(filters={"submission_id": submission_id})

    def get_by_submission_question(self, submission_id: UUID, question_id: UUID) -> AICorrection | None:
        """Busca correção de uma questão específica."""
        stmt = select(AICorrection).where(
            and_(AICorrection.submission_id == submission_id, AICorrection.question_id == question_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_pending_review(self) -> list[AICorrection]:
        """Busca correções que requerem revisão."""
        return self.get_all(filters={"requires_review": True, "status": AICorrectionStatus.COMPLETED})

    def get_by_status(self, status: AICorrectionStatus) -> list[AICorrection]:
        """Busca por status."""
        return self.get_all(filters={"status": status})

    def get_with_review(self, correction_id: UUID) -> AICorrection | None:
        """Busca correção com revisão carregada."""
        stmt = select(AICorrection).options(
            joinedload(AICorrection.reviews).joinedload(CorrectionReview.audit_logs),
        ).where(AICorrection.id == correction_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()


class CorrectionReviewRepository(BaseRepository[CorrectionReview]):
    """Repository para revisões de correção."""

    def __init__(self, db: Session):
        super().__init__(CorrectionReview, db)

    def get_by_ai_correction(self, ai_correction_id: UUID) -> CorrectionReview | None:
        """Busca revisão de uma correção."""
        return self.get_by_field("ai_correction_id", ai_correction_id)

    def get_by_reviewer(self, reviewer_id: UUID) -> list[CorrectionReview]:
        """Busca revisões de um revisor."""
        return self.get_all(filters={"reviewed_by": reviewer_id})

    def get_pending(self) -> list[CorrectionReview]:
        """Busca revisões pendentes."""
        return self.get_all(filters={"status": ReviewStatus.PENDING})


class CorrectionAuditLogRepository(BaseRepository[CorrectionAuditLog]):
    """Repository para logs de auditoria de correção."""

    def __init__(self, db: Session):
        super().__init__(CorrectionAuditLog, db)

    def get_by_review(self, review_id: UUID) -> list[CorrectionAuditLog]:
        """Busca logs de uma revisão."""
        stmt = select(CorrectionAuditLog).where(
            CorrectionAuditLog.review_id == review_id
        ).order_by(CorrectionAuditLog.changed_at)
        return list(self.db.execute(stmt).scalars().all())


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository para logs de auditoria geral."""

    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def log(
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
        """Cria log de auditoria."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=jsonable_encoder(old_values) if old_values is not None else None,
            new_values=jsonable_encoder(new_values) if new_values is not None else None,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            session_id=session_id,
            success=success,
            error_message=error_message,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def get_by_user(self, user_id: UUID, limit: int = 100) -> list[AuditLog]:
        """Busca logs de um usuário."""
        stmt = select(AuditLog).where(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_entity(self, entity_type: str, entity_id: UUID) -> list[AuditLog]:
        """Busca logs de uma entidade."""
        stmt = select(AuditLog).where(
            and_(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        ).order_by(AuditLog.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_action(self, action: AuditActionType, limit: int = 100) -> list[AuditLog]:
        """Busca logs por ação."""
        stmt = select(AuditLog).where(
            AuditLog.action == action
        ).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_recent(self, hours: int = 24, limit: int = 1000) -> list[AuditLog]:
        """Busca logs recentes."""
        from datetime import datetime, timedelta
        since = datetime.now(UTC) - timedelta(hours=hours)
        stmt = select(AuditLog).where(
            AuditLog.created_at >= since
        ).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())


class SystemLogRepository(BaseRepository[SystemLog]):
    """Repository para logs do sistema."""

    def __init__(self, db: Session):
        super().__init__(SystemLog, db)

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
        """Cria log do sistema."""
        log = SystemLog(
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
        self.db.add(log)
        self.db.flush()
        return log

    def get_errors(self, hours: int = 24, limit: int = 100) -> list[SystemLog]:
        """Busca logs de erro recentes."""
        from datetime import datetime, timedelta
        since = datetime.now(UTC) - timedelta(hours=hours)
        stmt = select(SystemLog).where(
            and_(SystemLog.level.in_(["ERROR", "CRITICAL"]), SystemLog.created_at >= since)
        ).order_by(SystemLog.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
