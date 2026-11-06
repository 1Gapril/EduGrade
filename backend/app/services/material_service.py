"""Serviço de materiais por disciplina, com autorização por vínculo acadêmico."""

import mimetypes
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from backend.app.models.academic import (
    Class,
    Enrollment,
    EnrollmentStatus,
    Subject,
    TeacherSubject,
)
from backend.app.models.material import StudyMaterial
from backend.app.models.user import Student, Teacher, User, UserRole

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".png", ".jpg", ".jpeg"}


class MaterialService:
    """Aplica as regras de acesso e persiste os arquivos de estudo."""

    def __init__(self, db: Session):
        self.db = db

    @property
    def storage_dir(self) -> Path:
        path = Path(settings.material_storage_dir)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / path
        return path.resolve()

    def _teacher_subject_ids(self, user_id: UUID) -> set[UUID]:
        statement = (
            select(TeacherSubject.subject_id)
            .join(Teacher, TeacherSubject.teacher_id == Teacher.id)
            .where(Teacher.user_id == user_id)
        )
        return set(self.db.execute(statement).scalars().all())

    def available_subjects(self, user: User) -> list[Subject]:
        statement = select(Subject).order_by(Subject.name)
        if user.role != UserRole.ADMIN:
            subject_ids = self._teacher_subject_ids(user.id)
            if not subject_ids:
                return []
            statement = statement.where(Subject.id.in_(subject_ids))
        return list(self.db.execute(statement).scalars().all())

    def list_for_teacher(
        self,
        user: User,
        subject_id: UUID | None = None,
    ) -> list[StudyMaterial]:
        statement = select(StudyMaterial).order_by(StudyMaterial.created_at.desc())
        if user.role != UserRole.ADMIN:
            subject_ids = self._teacher_subject_ids(user.id)
            if subject_id is not None and subject_id not in subject_ids:
                raise AuthorizationError("Você não está cadastrado nesta disciplina.")
            if not subject_ids:
                return []
            statement = statement.where(StudyMaterial.subject_id.in_(subject_ids))
        elif subject_id is not None:
            statement = statement.where(StudyMaterial.subject_id == subject_id)
        return list(self.db.execute(statement).scalars().all())

    def list_for_student(self, user_id: UUID) -> list[StudyMaterial]:
        statement = (
            select(StudyMaterial)
            .join(Subject, StudyMaterial.subject_id == Subject.id)
            .join(Class, Class.subject_id == Subject.id)
            .join(Enrollment, Enrollment.class_id == Class.id)
            .join(Student, Enrollment.student_id == Student.id)
            .where(
                Student.user_id == user_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .order_by(StudyMaterial.created_at.desc())
        )
        return list(self.db.execute(statement).scalars().unique().all())

    def can_access(self, material: StudyMaterial, user: User) -> bool:
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.TEACHER:
            return material.subject_id in self._teacher_subject_ids(user.id)
        if user.role == UserRole.STUDENT:
            statement = (
                select(Enrollment.id)
                .join(Student, Enrollment.student_id == Student.id)
                .join(Class, Enrollment.class_id == Class.id)
                .where(
                    Student.user_id == user.id,
                    Class.subject_id == material.subject_id,
                    Enrollment.status == EnrollmentStatus.ACTIVE,
                )
                .limit(1)
            )
            return self.db.execute(statement).first() is not None
        return False

    async def create(
        self,
        *,
        user: User,
        subject_id: UUID,
        title: str,
        description: str | None,
        upload: UploadFile,
    ) -> StudyMaterial:
        subject = self.db.get(Subject, subject_id)
        if subject is None:
            raise NotFoundError("Disciplina não encontrada.")
        if user.role != UserRole.ADMIN and subject_id not in self._teacher_subject_ids(user.id):
            raise AuthorizationError("Você precisa estar cadastrado nesta disciplina para publicar materiais.")

        original_filename = (upload.filename or "").replace("\\", "/").rsplit("/", 1)[-1]
        extension = Path(original_filename).suffix.lower()
        if not original_filename or extension not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Formato de arquivo não permitido. Use: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
            )

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        stored_filename = f"{uuid4().hex}{extension}"
        destination = self.storage_dir / stored_filename
        maximum_bytes = settings.max_upload_size_mb * 1024 * 1024
        file_size = 0

        try:
            with destination.open("wb") as target:
                while chunk := await upload.read(1024 * 1024):
                    file_size += len(chunk)
                    if file_size > maximum_bytes:
                        raise HTTPException(
                            status_code=413,
                            detail=f"O arquivo excede o limite de {settings.max_upload_size_mb} MB.",
                        )
                    target.write(chunk)
            if file_size == 0:
                raise ValidationError("O arquivo enviado está vazio.")
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

        material = StudyMaterial(
            subject_id=subject_id,
            uploaded_by=user.id,
            title=title.strip(),
            description=description.strip() if description and description.strip() else None,
            original_filename=original_filename,
            stored_filename=stored_filename,
            media_type=mimetypes.guess_type(original_filename)[0] or "application/octet-stream",
            file_size=file_size,
        )
        self.db.add(material)
        try:
            self.db.flush()
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return material

    def get_download(self, material_id: UUID, user: User) -> tuple[StudyMaterial, Path]:
        material = self.db.get(StudyMaterial, material_id)
        if material is None:
            raise NotFoundError("Material não encontrado.")
        if not self.can_access(material, user):
            raise AuthorizationError("Você não tem acesso a este material.")

        path = (self.storage_dir / material.stored_filename).resolve()
        if path.parent != self.storage_dir or not path.is_file():
            raise NotFoundError("Arquivo do material não encontrado.")
        return material, path

    def remove_file(self, material: StudyMaterial) -> None:
        (self.storage_dir / material.stored_filename).unlink(missing_ok=True)
