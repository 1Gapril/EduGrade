"""Serviço de tarefas de longa duração (barra global de progresso).

O backend é a fonte oficial do progresso: cada operação é registrada em
``operation_jobs`` e consultada pelo frontend. O percentual só é calculado
quando existe uma medida real (registros processados / total, questões
corrigidas etc.); caso contrário permanece ``None`` (indeterminado).
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.exceptions import NotFoundError
from backend.app.models.operation_job import (
    TERMINAL_STATUSES,
    OperationJob,
    OperationKind,
    OperationStatus,
)
from backend.app.models.user import User, UserRole

logger = logging.getLogger("edugrade.jobs")

TERMINAL_STATUS_VALUES = {status.value for status in TERMINAL_STATUSES}


class OperationCancelled(Exception):
    """Sinaliza que a operação foi cancelada pelo usuário."""


def _now() -> datetime:
    return datetime.now(UTC)


class OperationJobService:
    """Cria, atualiza e consulta operações acompanhadas pelo ProgressManager."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ criação
    def create(
        self,
        *,
        kind: OperationKind,
        title: str,
        user_id: UUID,
        payload: dict | None = None,
        total: int = 0,
        progress: float | None = None,
        step_key: str | None = None,
        step_label: str | None = None,
        status: OperationStatus = OperationStatus.PENDING,
    ) -> OperationJob:
        job = OperationJob(
            kind=kind,
            title=title[:255],
            status=status,
            payload=payload or {},
            total=max(0, int(total)),
            progress=progress,
            step_key=step_key,
            step_label=step_label,
            created_by=user_id,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        logger.info("Operação %s criada: %s (%s)", kind.value, job.id, title)
        return job

    # ---------------------------------------------------------------- consulta
    def get(self, job_id: UUID) -> OperationJob:
        job = self.db.get(OperationJob, job_id)
        if job is None:
            raise NotFoundError("Operação não encontrada")
        return job

    def get_for_user(self, job_id: UUID, user: User) -> OperationJob:
        """Retorna a operação apenas para o dono ou um administrador."""
        job = self.get(job_id)
        if job.created_by != user.id and user.role != UserRole.ADMIN:
            # Não revela a existência de operações de outros usuários.
            raise NotFoundError("Operação não encontrada")
        return job

    def list_recent(self, user: User, limit: int = 20) -> list[OperationJob]:
        query = self.db.query(OperationJob)
        if user.role != UserRole.ADMIN:
            query = query.filter(OperationJob.created_by == user.id)
        return (
            query.order_by(OperationJob.created_at.desc()).limit(max(1, min(limit, 100))).all()
        )

    # --------------------------------------------------------------- atualização
    def start(
        self,
        job_id: UUID,
        *,
        step_key: str | None = None,
        step_label: str | None = None,
        progress: float | None = None,
    ) -> OperationJob:
        job = self.get(job_id)
        job.status = OperationStatus.RUNNING
        job.started_at = job.started_at or _now()
        if step_key is not None:
            job.step_key = step_key
        if step_label is not None:
            job.step_label = step_label
        job.progress = progress
        job.updated_at = _now()
        self.db.commit()
        return job

    def set_step(
        self,
        job_id: UUID,
        *,
        step_key: str,
        step_label: str,
        progress: float | None = None,
        total: int | None = None,
    ) -> OperationJob:
        """Avança para uma nova etapa. ``progress=None`` = indeterminado."""
        job = self.get(job_id)
        job.step_key = step_key
        job.step_label = step_label
        job.progress = progress
        if total is not None:
            job.total = max(0, int(total))
        job.updated_at = _now()
        self.db.commit()
        if job.cancel_requested:
            raise OperationCancelled(step_label)
        return job

    def set_progress(
        self,
        job_id: UUID,
        *,
        processed: int | None = None,
        total: int | None = None,
        progress: float | None = None,
        succeeded: int | None = None,
        failed: int | None = None,
        skipped: int | None = None,
        step_label: str | None = None,
    ) -> OperationJob:
        """Atualiza contadores e percentual real. Cancela se solicitado."""
        job = self.get(job_id)
        if processed is not None:
            job.processed = max(0, int(processed))
        if total is not None:
            job.total = max(0, int(total))
        if succeeded is not None:
            job.succeeded = max(0, int(succeeded))
        if failed is not None:
            job.failed = max(0, int(failed))
        if skipped is not None:
            job.skipped = max(0, int(skipped))
        if step_label is not None:
            job.step_label = step_label
        if progress is not None:
            job.progress = progress
        elif job.total > 0:
            job.progress = round(job.processed / job.total * 100, 2)
        job.updated_at = _now()
        self.db.commit()
        if job.cancel_requested:
            raise OperationCancelled(job.step_label or "Operação cancelada")
        return job

    def add_warning(self, job_id: UUID, message: str) -> None:
        job = self.get(job_id)
        job.warnings = list(job.warnings or []) + [message]
        job.updated_at = _now()
        self.db.commit()

    def fail(
        self,
        job_id: UUID,
        message: str,
        *,
        error: str | None = None,
        result: dict | None = None,
    ) -> OperationJob:
        job = self.get(job_id)
        job.status = OperationStatus.FAILED
        job.message = message
        job.error = error or message
        if result is not None:
            job.result = result
        job.progress = None
        job.finished_at = _now()
        job.updated_at = _now()
        self.db.commit()
        logger.warning("Operação %s falhou: %s", job_id, message)
        return job

    def cancel(self, job_id: UUID) -> OperationJob:
        job = self.get(job_id)
        if job.status in TERMINAL_STATUSES:
            return job
        job.cancel_requested = True
        job.status = OperationStatus.CANCELLED
        job.message = "Operação cancelada pelo usuário."
        job.progress = None
        job.finished_at = _now()
        job.updated_at = _now()
        self.db.commit()
        return job

    def finish(
        self,
        job_id: UUID,
        *,
        message: str,
        result: dict | None = None,
        with_warnings: bool = False,
    ) -> OperationJob:
        job = self.get(job_id)
        job.status = (
            OperationStatus.SUCCEEDED_WITH_WARNINGS if with_warnings else OperationStatus.SUCCEEDED
        )
        job.message = message
        job.result = result
        job.progress = 100.0
        if job.total > 0:
            job.processed = job.total
        job.finished_at = _now()
        job.updated_at = _now()
        self.db.commit()
        logger.info("Operação %s concluída: %s", job_id, message)
        return job

    def mark_cancelled(self, job_id: UUID, message: str = "Operação cancelada.") -> OperationJob:
        job = self.get(job_id)
        job.status = OperationStatus.CANCELLED
        job.message = message
        job.progress = None
        job.cancel_requested = True
        job.finished_at = _now()
        job.updated_at = _now()
        self.db.commit()
        return job

    def is_cancelled(self, job_id: UUID) -> bool:
        job = self.db.get(OperationJob, job_id)
        return bool(job and job.cancel_requested)

    # ---------------------------------------------------------------- serialização
    @staticmethod
    def elapsed_seconds(job: OperationJob) -> float:
        if job.started_at is None:
            return 0.0
        # O SQLite devolve datetimes sem timezone; normaliza para UTC.
        started = job.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=UTC)
        end = job.finished_at or _now()
        if end.tzinfo is None:
            end = end.replace(tzinfo=UTC)
        return round(max(0.0, (end - started).total_seconds()), 1)

    @classmethod
    def serialize(cls, job: OperationJob) -> dict:
        return {
            "id": str(job.id),
            "kind": job.kind.value if hasattr(job.kind, "value") else str(job.kind),
            "title": job.title,
            "status": job.status.value if hasattr(job.status, "value") else str(job.status),
            "step_key": job.step_key,
            "step_label": job.step_label,
            "progress": job.progress,
            "processed": job.processed,
            "total": job.total,
            "succeeded": job.succeeded,
            "failed": job.failed,
            "skipped": job.skipped,
            "message": job.message,
            "error": job.error,
            "warnings": list(job.warnings or []),
            "payload": job.payload or {},
            "result": job.result,
            "cancel_requested": job.cancel_requested,
            "can_cancel": (
                job.status not in TERMINAL_STATUSES and not job.cancel_requested
            ),
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "elapsed_seconds": cls.elapsed_seconds(job),
        }
