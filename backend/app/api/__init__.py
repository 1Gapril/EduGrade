"""API Routes package initialization."""

from backend.app.api.routes import academic, ai_correction, audit, auth, batch_grading, exams, users

__all__ = ["auth", "users", "academic", "exams", "ai_correction", "audit", "batch_grading"]
