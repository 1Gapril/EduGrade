from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from backend.app.api.routes import batch_grading
from backend.app.models.grading_batch import BatchStatus, FileStatus


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
