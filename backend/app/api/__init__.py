"""API Routes package initialization."""

from backend.app.api.routes import auth, users, academic, exams, ai_correction, audit, batch_grading

__all__ = ["auth", "users", "academic", "exams", "ai_correction", "audit", "batch_grading"]