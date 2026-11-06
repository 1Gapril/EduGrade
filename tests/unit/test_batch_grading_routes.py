from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from backend.app.api.routes import batch_grading
from backend.app.models.grading_batch import BatchStatus, FileStatus
from backend.app.models.user import UserRole
from backend.app.schemas.grading_batch import GradingBatchCreate, StudentIdentificationUpdate


class _Upload:
    def __init__(self, filename: str, content: bytes = b"data"):
        self.filename = filename
        self.content_type = "application/pdf"
        self.content = content

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_batch_upload_persists_success_and_failure_per_file(monkeypatch, tmp_path):
    class Storage:
        async def save(self, upload, folder):
            if upload.filename == "invalid.txt":
                raise HTTPException(status_code=400, detail="Formato não permitido")
            path = tmp_path / upload.filename
            path.write_bytes(upload.content)
            return str(path)

    batch = SimpleNamespace(status=BatchStatus.UPLOADING)
    monkeypatch.setattr(batch_grading, "FileStorage", Storage)
    monkeypatch.setattr(batch_grading, "_assert_batch_access", lambda *args, **kwargs: batch)
    service = SimpleNamespace(db=MagicMock(), add_files=MagicMock(return_value=[]))
    user = SimpleNamespace(id=uuid4())

    await batch_grading.add_files(
        uuid4(),
        [_Upload("valid.pdf"), _Upload("invalid.txt")],
        current_user=user,
        service=service,
    )

    records = service.add_files.call_args.args[1]
    assert records[0]["status"] is FileStatus.PENDING
    assert records[0]["size"] == len(b"data")
    assert Path(records[0]["path"]).exists()
    assert records[1]["status"] is FileStatus.FAILED
    assert records[1]["path"] == ""
    assert records[1]["error_message"] == "Formato não permitido"
    assert service.add_files.call_args.kwargs["uploaded_by"] == user.id
    service.db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_batch_creation_checks_upload_permission_and_matching_version(monkeypatch):
    exam_id, version_id, user_id = uuid4(), uuid4(), uuid4()
    user = SimpleNamespace(id=user_id)
    batch = SimpleNamespace(exam_id=exam_id)
    service = SimpleNamespace(db=MagicMock(), create_batch=MagicMock(return_value=batch))
    monkeypatch.setattr(batch_grading, "_assert_exam_access", MagicMock())
    version_check = MagicMock(return_value=SimpleNamespace(exam_id=exam_id))
    monkeypatch.setattr(batch_grading, "_assert_version_access", version_check)

    result = await batch_grading.create_batch(
        GradingBatchCreate(exam_id=exam_id, version_id=version_id),
        current_user=user,
        service=service,
    )

    assert result is batch
    version_check.assert_called_once_with(service.db, user, version_id, "upload_submissions")
    service.create_batch.assert_called_once_with(
        exam_id=exam_id,
        version_id=version_id,
        uploaded_by=user_id,
    )

    version_check.return_value = SimpleNamespace(exam_id=uuid4())
    with pytest.raises(HTTPException) as exc_info:
        await batch_grading.create_batch(
            GradingBatchCreate(exam_id=exam_id, version_id=version_id),
            current_user=user,
            service=service,
        )
    assert exc_info.value.status_code == 422
    assert service.create_batch.call_count == 1


@pytest.mark.asyncio
async def test_batch_listing_filters_and_paginates_for_admin():
    exam_id = uuid4()
    query = MagicMock()
    query.join.return_value = query
    query.filter.return_value = query
    query.count.return_value = 0
    query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
    service = SimpleNamespace(db=MagicMock())
    service.db.query.return_value = query

    result = await batch_grading.list_batches(
        exam_id=exam_id,
        status_filter=BatchStatus.UPLOADING,
        page=2,
        page_size=5,
        current_user=SimpleNamespace(role=UserRole.ADMIN),
        service=service,
    )

    assert result.items == []
    assert result.total == 0
    assert result.page == 2
    assert result.page_size == 5
    query.filter.assert_called()


@pytest.mark.asyncio
async def test_batch_processing_and_review_routes_delegate_with_context(monkeypatch):
    batch_id, user_id, identification_id, student_id = uuid4(), uuid4(), uuid4(), uuid4()
    user = SimpleNamespace(id=user_id)
    batch = SimpleNamespace(status=BatchStatus.PROCESSING)
    details = {
        "progress": {"percentage": 10},
        "file_stats": {},
        "submission_stats": {},
        "pending_identifications": 0,
    }
    service = SimpleNamespace(
        db=MagicMock(),
        start_processing=MagicMock(return_value=batch),
        process_batch_files=MagicMock(return_value=batch),
        identify_students=MagicMock(return_value=batch),
        group_pages=MagicMock(return_value=batch),
        create_submissions_from_groups=MagicMock(),
        get_batch=MagicMock(return_value=batch),
        get_batch_with_details=MagicMock(return_value=details),
        grade_all_submissions=AsyncMock(return_value=batch),
        get_pending_identifications=MagicMock(return_value=[]),
        manual_identify=MagicMock(return_value=SimpleNamespace(id=identification_id)),
        page_repo=object(),
        file_repo=object(),
    )
    monkeypatch.setattr(batch_grading, "_assert_batch_access", MagicMock(return_value=batch))

    assert await batch_grading.start_processing(batch_id, current_user=user, service=service) is batch
    assert await batch_grading.process_batch_pages(
        batch_id, current_user=user, service=service
    ) is batch
    assert await batch_grading.identify_students(
        batch_id, current_user=user, service=service
    ) is batch
    assert await batch_grading.group_pages(batch_id, current_user=user, service=service) is batch
    assert await batch_grading.create_submissions(
        batch_id, current_user=user, service=service
    ) is batch
    assert await batch_grading.grade_all(batch_id, current_user=user, service=service) is batch
    pending = await batch_grading.get_pending_identifications(
        batch_id, current_user=user, service=service
    )
    assert pending.total == 0
    progress = await batch_grading.get_progress(
        batch_id, current_user=user, service=service
    )
    assert progress.progress == details["progress"]

    ident = SimpleNamespace(page_id=uuid4())
    page = SimpleNamespace(batch_file_id=uuid4())
    file_record = SimpleNamespace(batch_id=batch_id)
    service.db.get.side_effect = [ident, page, file_record]
    reviewed = await batch_grading.manual_identify(
        identification_id,
        StudentIdentificationUpdate(student_id=student_id),
        current_user=user,
        service=service,
    )
    assert reviewed.id == identification_id
    service.manual_identify.assert_called_once_with(
        identification_id=identification_id,
        student_id=student_id,
        teacher_id=user_id,
    )
