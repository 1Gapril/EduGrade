"""Schemas para materiais didáticos."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MaterialSubjectResponse(BaseModel):
    id: UUID
    code: str
    name: str


class StudyMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_id: UUID
    subject_name: str
    title: str
    description: str | None = None
    original_filename: str
    file_size: int
    created_at: datetime
