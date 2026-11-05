"""Rotas de publicação e acesso a materiais de estudo por disciplina."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import (
    get_current_active_user,
    require_student,
    require_teacher_or_admin,
)
from backend.app.models.user import User
from backend.app.schemas.material import MaterialSubjectResponse, StudyMaterialResponse
from backend.app.services.material_service import MaterialService

router = APIRouter(prefix="/materials", tags=["Materiais de estudo"])


def _material_response(material) -> dict:
    return {
        "id": material.id,
        "subject_id": material.subject_id,
        "subject_name": material.subject.name,
        "title": material.title,
        "description": material.description,
        "original_filename": material.original_filename,
        "file_size": material.file_size,
        "created_at": material.created_at,
    }


@router.get("/teacher/subjects", response_model=list[MaterialSubjectResponse])
def list_teacher_subjects(
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Lista disciplinas atribuídas ao professor; administradores podem ver todas."""
    service = MaterialService(db)
    return [
        {"id": subject.id, "code": subject.code, "name": subject.name}
        for subject in service.available_subjects(current_user)
    ]


@router.get("/teacher", response_model=list[StudyMaterialResponse])
def list_teacher_materials(
    subject_id: UUID | None = Query(None),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = MaterialService(db)
    return [
        _material_response(material)
        for material in service.list_for_teacher(current_user, subject_id)
    ]


@router.post("", response_model=StudyMaterialResponse, status_code=status.HTTP_201_CREATED)
async def upload_material(
    subject_id: UUID = Form(...),
    title: str = Form(..., min_length=2, max_length=255),
    description: str | None = Form(None, max_length=5000),
    file: UploadFile = File(...),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = MaterialService(db)
    material = None
    try:
        material = await service.create(
            user=current_user,
            subject_id=subject_id,
            title=title,
            description=description,
            upload=file,
        )
        db.commit()
        db.refresh(material)
    except Exception:
        db.rollback()
        if material is not None:
            service.remove_file(material)
        raise
    return _material_response(material)


@router.get("/student", response_model=list[StudyMaterialResponse])
def list_student_materials(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """Lista materiais somente das disciplinas com matrícula ativa do aluno."""
    service = MaterialService(db)
    return [
        _material_response(material)
        for material in service.list_for_student(current_user.id)
    ]


@router.get("/{material_id}/download")
def download_material(
    material_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = MaterialService(db)
    material, path = service.get_download(material_id, current_user)
    return FileResponse(
        path,
        media_type=material.media_type,
        filename=material.original_filename,
    )
