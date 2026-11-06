"""Persistent snapshots of test and coverage runs."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class QualityRun(Base):
    """A distinct test/coverage report observed by the quality dashboard."""

    __tablename__ = "quality_runs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    run_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    coverage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    lines_valid: Mapped[int] = mapped_column(Integer, nullable=False)
    lines_covered: Mapped[int] = mapped_column(Integer, nullable=False)
    tests_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tests_passed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tests_failed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tests_skipped: Mapped[int | None] = mapped_column(Integer, nullable=True)
    html_report_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
