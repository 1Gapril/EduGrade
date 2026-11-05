from io import BytesIO
from pathlib import Path

import pymupdf
import pytest
from fastapi import HTTPException, UploadFile

from backend.app.core.config import settings
from backend.app.integrations import email
from backend.app.integrations.storage import FileStorage


@pytest.mark.asyncio
async def test_storage_saves_upload_with_generated_name(tmp_path, monkeypatch):
    monkeypatch.setitem(FileStorage._folders, "exams", str(tmp_path))
    upload = UploadFile(file=BytesIO(b"exam data"), filename="../../exam.PDF")

    saved_path = Path(await FileStorage().save(upload))

    assert saved_path.parent == tmp_path
    assert saved_path.suffix == ".pdf"
    assert saved_path.read_bytes() == b"exam data"
    assert upload.file.closed


@pytest.mark.asyncio
async def test_storage_rejects_upload_over_configured_limit(tmp_path, monkeypatch):
    monkeypatch.setitem(FileStorage._folders, "exams", str(tmp_path))
    monkeypatch.setattr(settings, "max_upload_size_mb", 0)
    upload = UploadFile(file=BytesIO(b"larger than zero"), filename="exam.pdf")

    with pytest.raises(HTTPException) as error:
        await FileStorage().save(upload)

    assert error.value.status_code == 413
    assert list(tmp_path.iterdir()) == []
    assert upload.file.closed


@pytest.mark.asyncio
async def test_storage_rejects_unsupported_extension(tmp_path, monkeypatch):
    monkeypatch.setitem(FileStorage._folders, "exams", str(tmp_path))
    upload = UploadFile(file=BytesIO(b"not an exam"), filename="exam.exe")

    with pytest.raises(HTTPException) as error:
        await FileStorage().save(upload)

    assert error.value.status_code == 400
    assert list(tmp_path.iterdir()) == []


def test_storage_expands_pdf_into_page_images(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    monkeypatch.setitem(FileStorage._folders, "processed", str(processed))
    pdf_path = tmp_path / "exam.pdf"
    document = pymupdf.open()
    document.new_page()
    document.new_page()
    document.save(pdf_path)
    document.close()

    page_paths = FileStorage().expand_pdf_pages(str(pdf_path))

    assert len(page_paths) == 2
    assert all(Path(path).is_file() and Path(path).suffix == ".png" for path in page_paths)


def test_storage_rejects_corrupted_pdf(tmp_path):
    pdf_path = tmp_path / "corrupted.pdf"
    pdf_path.write_bytes(b"not a PDF")

    with pytest.raises(HTTPException) as error:
        FileStorage().expand_pdf_pages(str(pdf_path))

    assert error.value.status_code == 400


def test_email_requires_smtp_configuration(monkeypatch):
    monkeypatch.setattr(settings, "smtp_host", None)

    with pytest.raises(email.EmailDeliveryError, match="SMTP não está configurado"):
        email.send_account_credentials("person@example.test", "Pessoa", "user", "temporary")


def test_email_rejects_partial_smtp_authentication(monkeypatch):
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.test")
    monkeypatch.setattr(settings, "smtp_user", "mailer")
    monkeypatch.setattr(settings, "smtp_password", None)

    with pytest.raises(email.EmailDeliveryError, match="autenticação SMTP está incompleta"):
        email.send_account_credentials("person@example.test", "Pessoa", "user", "temporary")


@pytest.mark.parametrize("port", [465, 587])
def test_email_sends_using_configured_tls_mode(monkeypatch, port):
    class SMTPServer:
        def __init__(self):
            self.messages = []
            self.logins = []
            self.starttls_calls = 0

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def login(self, username, password):
            self.logins.append((username, password))

        def send_message(self, message):
            self.messages.append(message)

        def ehlo(self):
            return None

        def starttls(self, **_kwargs):
            self.starttls_calls += 1

    server = SMTPServer()
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.test")
    monkeypatch.setattr(settings, "smtp_port", port)
    monkeypatch.setattr(settings, "smtp_user", "mailer")
    monkeypatch.setattr(settings, "smtp_password", "temporary-secret")
    monkeypatch.setattr(email.ssl, "create_default_context", lambda: object())
    monkeypatch.setattr(email.smtplib, "SMTP_SSL", lambda *_args, **_kwargs: server)
    monkeypatch.setattr(email.smtplib, "SMTP", lambda *_args, **_kwargs: server)

    email.send_account_credentials("person@example.test", "Pessoa", "user", "temporary")

    assert len(server.messages) == 1
    assert server.messages[0]["To"] == "person@example.test"
    assert server.logins == [("mailer", "temporary-secret")]
    assert server.starttls_calls == (0 if port == 465 else 1)


def test_email_wraps_smtp_delivery_errors(monkeypatch):
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.test")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_user", None)
    monkeypatch.setattr(settings, "smtp_password", None)

    def fail_to_connect(*_args, **_kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr(email.smtplib, "SMTP", fail_to_connect)

    with pytest.raises(email.EmailDeliveryError, match="Não foi possível enviar"):
        email.send_account_credentials("person@example.test", "Pessoa", "user", "temporary")
