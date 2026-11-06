from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, UploadFile

from backend.app.core.config import settings
from backend.app.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from backend.app.models.academic import Subject
from backend.app.models.material import StudyMaterial
from backend.app.models.user import UserRole
from backend.app.services.material_service import MaterialService


class Result:
    def __init__(self, rows=(), first=None):
        self.rows = list(rows)
        self.first_row = first

    def scalars(self):
        return self

    def unique(self):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.first_row


class FakeDb:
    def __init__(self, result=None, objects=None, flush_error=None):
        self.result = result or Result()
        self.objects = objects or {}
        self.added = []
        self.flush_error = flush_error

    def execute(self, _statement):
        return self.result

    def get(self, model, key):
        return self.objects.get((model, key))

    def add(self, value):
        self.added.append(value)

    def flush(self):
        if self.flush_error:
            raise self.flush_error


def make_user(role, user_id=None):
    return SimpleNamespace(id=user_id or uuid4(), role=role)


def test_storage_dir_resolves_relative_and_absolute_paths(monkeypatch, tmp_path):
    service = MaterialService(FakeDb())
    relative = Path("materials")
    monkeypatch.setattr(settings, "material_storage_dir", str(relative))
    assert service.storage_dir == (Path(__file__).resolve().parents[2] / relative).resolve()

    monkeypatch.setattr(settings, "material_storage_dir", str(tmp_path))
    assert service.storage_dir == tmp_path.resolve()


def test_available_subjects_limits_teachers_and_allows_admins(monkeypatch):
    subject_id = uuid4()
    subjects = [SimpleNamespace(id=subject_id), SimpleNamespace(id=uuid4())]
    service = MaterialService(FakeDb(Result(subjects)))
    teacher = make_user(UserRole.TEACHER)
    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: {subject_id})

    assert service.available_subjects(teacher) == subjects
    assert service.available_subjects(make_user(UserRole.ADMIN)) == subjects

    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: set())
    assert service.available_subjects(teacher) == []


def test_list_for_teacher_applies_role_and_subject_filter(monkeypatch):
    materials = [SimpleNamespace(id=uuid4())]
    service = MaterialService(FakeDb(Result(materials)))
    teacher = make_user(UserRole.TEACHER)
    subject_id = uuid4()
    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: {subject_id})

    assert service.list_for_teacher(teacher) == materials
    assert service.list_for_teacher(make_user(UserRole.ADMIN), subject_id) == materials
    assert service.list_for_teacher(teacher) == materials

    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: set())
    assert service.list_for_teacher(teacher) == []
    with pytest.raises(AuthorizationError):
        service.list_for_teacher(teacher, subject_id)


def test_list_for_student_returns_unique_results():
    materials = [SimpleNamespace(id=uuid4())]
    service = MaterialService(FakeDb(Result(materials)))

    assert service.list_for_student(uuid4()) == materials


def test_can_access_for_admin_teacher_student_and_unknown_role(monkeypatch):
    subject_id = uuid4()
    material = SimpleNamespace(subject_id=subject_id)
    service = MaterialService(FakeDb(Result(first=object())))
    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: {subject_id})

    assert service.can_access(material, make_user(UserRole.ADMIN))
    assert service.can_access(material, make_user(UserRole.TEACHER))
    assert service.can_access(material, make_user(UserRole.STUDENT))
    assert not service.can_access(material, make_user("unknown"))

    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: set())
    assert not service.can_access(material, make_user(UserRole.TEACHER))
    service.db.result = Result(first=None)
    assert not service.can_access(material, make_user(UserRole.STUDENT))


@pytest.mark.asyncio
async def test_create_sanitizes_filename_persists_metadata_and_closes_upload(monkeypatch, tmp_path):
    subject_id = uuid4()
    user = make_user(UserRole.TEACHER)
    db = FakeDb(objects={(Subject, subject_id): SimpleNamespace(id=subject_id)})
    service = MaterialService(db)
    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: {subject_id})
    monkeypatch.setattr(settings, "material_storage_dir", str(tmp_path))
    upload = UploadFile(file=BytesIO(b"course notes"), filename=r"..\private\notes.TXT")

    material = await service.create(
        user=user,
        subject_id=subject_id,
        title="  Notes  ",
        description="  useful details  ",
        upload=upload,
    )

    assert material.title == "Notes"
    assert material.description == "useful details"
    assert material.original_filename == "notes.TXT"
    assert material.media_type == "text/plain"
    assert material.file_size == len(b"course notes")
    assert material in db.added
    assert (tmp_path / material.stored_filename).read_bytes() == b"course notes"
    assert upload.file.closed


@pytest.mark.asyncio
async def test_create_rejects_missing_subject_unassigned_teacher_and_bad_extension(tmp_path, monkeypatch):
    subject_id = uuid4()
    user = make_user(UserRole.TEACHER)
    service = MaterialService(FakeDb())
    monkeypatch.setattr(settings, "material_storage_dir", str(tmp_path))

    with pytest.raises(NotFoundError):
        await service.create(
            user=user,
            subject_id=subject_id,
            title="Notes",
            description=None,
            upload=UploadFile(file=BytesIO(b"x"), filename="notes.txt"),
        )

    service.db.objects[(Subject, subject_id)] = SimpleNamespace(id=subject_id)
    monkeypatch.setattr(service, "_teacher_subject_ids", lambda _user_id: set())
    with pytest.raises(AuthorizationError):
        await service.create(
            user=user,
            subject_id=subject_id,
            title="Notes",
            description=None,
            upload=UploadFile(file=BytesIO(b"x"), filename="notes.txt"),
        )

    admin = make_user(UserRole.ADMIN)
    with pytest.raises(ValidationError, match="Formato de arquivo"):
        await service.create(
            user=admin,
            subject_id=subject_id,
            title="Notes",
            description=None,
            upload=UploadFile(file=BytesIO(b"x"), filename="notes.exe"),
        )


@pytest.mark.asyncio
async def test_create_cleans_up_empty_oversized_and_failed_flush_files(monkeypatch, tmp_path):
    subject_id = uuid4()
    user = make_user(UserRole.ADMIN)
    monkeypatch.setattr(settings, "material_storage_dir", str(tmp_path))
    monkeypatch.setattr(settings, "max_upload_size_mb", 0)

    empty_service = MaterialService(
        FakeDb(objects={(Subject, subject_id): SimpleNamespace(id=subject_id)})
    )
    with pytest.raises(ValidationError, match="vazio"):
        await empty_service.create(
            user=user,
            subject_id=subject_id,
            title="Notes",
            description=" ",
            upload=UploadFile(file=BytesIO(b""), filename="empty.txt"),
        )
    assert list(tmp_path.iterdir()) == []

    oversized_service = MaterialService(
        FakeDb(objects={(Subject, subject_id): SimpleNamespace(id=subject_id)})
    )
    with pytest.raises(HTTPException) as error:
        await oversized_service.create(
            user=user,
            subject_id=subject_id,
            title="Notes",
            description=None,
            upload=UploadFile(file=BytesIO(b"too large"), filename="large.txt"),
        )
    assert error.value.status_code == 413
    assert list(tmp_path.iterdir()) == []

    monkeypatch.setattr(settings, "max_upload_size_mb", 1)
    failed_flush_service = MaterialService(
        FakeDb(
            objects={(Subject, subject_id): SimpleNamespace(id=subject_id)},
            flush_error=RuntimeError("database unavailable"),
        )
    )
    with pytest.raises(RuntimeError, match="database unavailable"):
        await failed_flush_service.create(
            user=user,
            subject_id=subject_id,
            title="Notes",
            description=" ",
            upload=UploadFile(file=BytesIO(b"valid file"), filename="notes.txt"),
        )
    assert list(tmp_path.iterdir()) == []


def test_get_download_checks_existence_access_and_file_path(monkeypatch, tmp_path):
    material_id = uuid4()
    subject_id = uuid4()
    material = SimpleNamespace(
        id=material_id,
        subject_id=subject_id,
        stored_filename="notes.txt",
    )
    service = MaterialService(FakeDb(objects={(StudyMaterial, material_id): material}))
    user = make_user(UserRole.ADMIN)
    monkeypatch.setattr(settings, "material_storage_dir", str(tmp_path))

    with pytest.raises(NotFoundError, match="Arquivo"):
        service.get_download(material_id, user)
    (tmp_path / "notes.txt").write_text("notes", encoding="utf-8")
    assert service.get_download(material_id, user) == (material, tmp_path / "notes.txt")

    material.stored_filename = "../outside.txt"
    with pytest.raises(NotFoundError, match="Arquivo"):
        service.get_download(material_id, user)

    denied = make_user(UserRole.STUDENT)
    monkeypatch.setattr(service, "can_access", lambda _material, _user: False)
    with pytest.raises(AuthorizationError):
        service.get_download(material_id, denied)

    service.db.objects.clear()
    with pytest.raises(NotFoundError, match="Material"):
        service.get_download(material_id, user)


def test_remove_file_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "material_storage_dir", str(tmp_path))
    path = tmp_path / "existing.txt"
    path.write_text("notes", encoding="utf-8")
    service = MaterialService(FakeDb())
    material = SimpleNamespace(stored_filename=path.name)

    service.remove_file(material)
    service.remove_file(material)

    assert not path.exists()
