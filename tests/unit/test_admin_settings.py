
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.config import settings
from backend.app.core.database import Base, get_db
from backend.app.core.security import get_current_active_user
from backend.app.main import app
from backend.app.models.admin_settings import AIProviderConfig
from backend.app.models.user import User, UserRole
from backend.app.services import admin_settings_service


@pytest.fixture
def admin_api(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)
    session = test_session()
    admin = User(
        email="settings-admin@example.test",
        username="settings-admin",
        hashed_password="not-a-real-password",
        full_name="Settings Admin",
        role=UserRole.ADMIN,
    )
    teacher = User(
        email="settings-teacher@example.test",
        username="settings-teacher",
        hashed_password="not-a-real-password",
        full_name="Settings Teacher",
        role=UserRole.TEACHER,
    )
    session.add_all([admin, teacher])
    session.commit()
    actor = [admin]

    def override_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    def override_user():
        return actor[0]

    overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_active_user] = override_user
    key_before = settings.credential_encryption_key
    monkeypatch.setattr(settings, "credential_encryption_key", Fernet.generate_key().decode())
    client = TestClient(app, raise_server_exceptions=False)
    yield client, actor, admin, teacher, test_session
    client.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(overrides)
    settings.credential_encryption_key = key_before
    session.close()
    engine.dispose()


def test_provider_crud_encrypts_key_masks_response_and_audits_without_secret(admin_api):
    client, actor, admin, teacher, test_session = admin_api
    secret = "nim-test-secret-do-not-return"
    payload = {
        "provider_id": "nvidia_nim",
        "provider_type": "nvidia_nim",
        "name": "NVIDIA NIM teste",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": secret,
        "model": "nvidia/test-model",
        "is_enabled": True,
    }

    response = client.post("/api/v1/admin/settings/providers", json=payload)

    assert response.status_code == 201
    assert secret not in response.text
    assert response.json()["api_key_masked"] == f"••••{secret[-4:]}"
    with test_session() as db:
        row = db.execute(
            select(AIProviderConfig).where(AIProviderConfig.provider_id == "nvidia_nim")
        ).scalar_one()
        audit = db.execute(
            select(admin_settings_service.AuditLog).where(
                admin_settings_service.AuditLog.entity_type == "AdminSettings"
            )
        ).scalar_one()
        assert row.encrypted_api_key != secret
        assert secret not in audit.description
        assert secret not in str(audit.old_values)
        assert secret not in str(audit.new_values)

    actor[0] = teacher
    assert client.get("/api/v1/admin/settings/providers").status_code == 403

    actor[0] = admin
    updated = client.put(
        "/api/v1/admin/settings/providers/nvidia_nim",
        json={"model": "nvidia/updated-model"},
    )
    assert updated.status_code == 200
    assert secret not in updated.text
    assert updated.json()["model"] == "nvidia/updated-model"
    removed = client.delete("/api/v1/admin/settings/providers/nvidia_nim")
    assert removed.status_code == 204


def test_provider_test_records_real_successful_models(admin_api, monkeypatch):
    client, _, _, _, _ = admin_api

    class FakeResponse:
        status_code = 200
        is_success = True

        def json(self):
            return {"data": [{"id": "nvidia/model-one"}, {"id": "nvidia/model-two"}]}

        def raise_for_status(self):
            pass

    class FakeAsyncClient:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, url, headers):
            assert url.endswith("/models")
            assert headers["Authorization"].startswith("Bearer ")
            return FakeResponse()

    monkeypatch.setattr(admin_settings_service.httpx, "AsyncClient", FakeAsyncClient)
    created = client.post(
        "/api/v1/admin/settings/providers",
        json={
            "provider_id": "nim-test",
            "provider_type": "nvidia_nim",
            "name": "NIM teste",
            "base_url": "https://integrate.api.nvidia.com/v1",
            "api_key": "test-key-not-real",
        },
    )
    assert created.status_code == 201

    tested = client.post("/api/v1/admin/settings/providers/nim-test/test")

    assert tested.status_code == 200
    assert tested.json()["status"] == "connected"
    assert tested.json()["available_models"] == ["nvidia/model-one", "nvidia/model-two"]


def test_credential_vault_requires_a_bootstrap_key(monkeypatch):
    monkeypatch.setattr(settings, "credential_encryption_key", None)

    with pytest.raises(Exception) as error:
        admin_settings_service._encrypt_credential("sensitive")

    assert getattr(error.value, "status_code", None) == 503
    assert "CREDENTIAL_ENCRYPTION_KEY" in str(error.value)


def test_custom_provider_rejects_private_ip_endpoints():
    with pytest.raises(Exception) as error:
        admin_settings_service._validate_provider_url(
            "custom",
            "openai",
            "https://127.0.0.1:8080/v1",
        )

    assert getattr(error.value, "status_code", None) == 422


def test_fcc_url_normalizes_admin_root_and_rejects_other_paths():
    assert (
        admin_settings_service._validate_fcc_url("http://127.0.0.1:8082/admin/")
        == "http://127.0.0.1:8082"
    )
    assert (
        admin_settings_service._validate_fcc_url("http://127.0.0.1:8082/")
        == "http://127.0.0.1:8082"
    )

    with pytest.raises(Exception) as error:
        admin_settings_service._validate_fcc_url("http://127.0.0.1:8082/admin/api")

    assert getattr(error.value, "status_code", None) == 422
