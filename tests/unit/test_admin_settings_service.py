from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import httpx
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings
from backend.app.core.database import Base
from backend.app.models.admin_settings import AdminSetting, AIProviderConfig
from backend.app.models.user import User
from backend.app.services import admin_settings_service as admin_service
from backend.app.services.admin_settings_service import AdminSettingsService


@pytest.mark.parametrize(
    ("provider_type", "payload", "expected"),
    [
        ("ollama", {"models": [{"name": "z"}, {"name": "a"}, {"name": "a"}, "skip"]}, ["a", "z"]),
        (
            "google_gemini",
            {
                "models": [
                    {"name": "models/b", "supportedGenerationMethods": ["generateContent"]},
                    {"name": "models/a", "supportedGenerationMethods": ["embed"]},
                    {"name": "models/c", "supportedGenerationMethods": ["generateContent"]},
                ]
            },
            ["models/b", "models/c"],
        ),
        ("openai", {"data": [{"id": "z"}, {"id": "a"}, {"name": "ignored"}]}, ["a", "z"]),
        ("openai", [], []),
    ],
)
def test_provider_model_parsing(provider_type, payload, expected):
    provider = SimpleNamespace(provider_type=provider_type, base_url="https://api.example.test/v1")

    assert admin_service._extract_models(provider, payload) == expected


@pytest.mark.parametrize(
    ("provider_type", "base_url", "endpoint", "headers"),
    [
        (
            "ollama",
            "http://localhost:11434",
            "http://localhost:11434/api/tags",
            {"Authorization": "Bearer api-key"},
        ),
        (
            "google_gemini",
            "https://generativelanguage.googleapis.com",
            "https://generativelanguage.googleapis.com/v1beta/models",
            {},
        ),
        ("anthropic", "https://api.anthropic.com", "https://api.anthropic.com/v1/models", {}),
        (
            "openai",
            "https://api.openai.com/v1",
            "https://api.openai.com/v1/models",
            {"Authorization": "Bearer api-key"},
        ),
    ],
)
def test_provider_endpoint_and_auth_header_helpers(provider_type, base_url, endpoint, headers):
    provider = SimpleNamespace(provider_type=provider_type, base_url=base_url)
    assert admin_service._models_endpoint(provider) == endpoint
    assert admin_service._provider_headers(provider, None) == {}
    with_key = admin_service._provider_headers(provider, "api-key")
    if provider_type == "anthropic":
        assert with_key == {"x-api-key": "api-key", "anthropic-version": "2023-06-01"}
    elif provider_type == "google_gemini":
        assert with_key == {"x-goog-api-key": "api-key"}
    else:
        assert with_key == headers


def test_runtime_and_fcc_settings_persist_updates(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'settings.db'}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    user = User(
        email="admin@example.test",
        username="admin",
        hashed_password="not-a-real-password",
        full_name="Test Admin",
    )
    db.add(user)
    db.flush()
    try:
        monkeypatch.setattr(settings, "ai_timeout_seconds", 60)
        service = AdminSettingsService(db)
        assert service.get_runtime_settings()["ai_timeout_seconds"] == 60

        updated = service.update_runtime_settings({"ai_timeout_seconds": 25}, user)
        assert updated["ai_timeout_seconds"] == 25
        assert settings.ai_timeout_seconds == 25
        row = db.get(AdminSetting, "ai_timeout_seconds")
        assert row.value == 25
        assert row.updated_by == user.id

        assert service.fcc_base_url() == settings.fcc_base_url
        monkeypatch.setattr(
            admin_service.settings,
            "fcc_base_url",
            "http://127.0.0.1:8082",
        )
        assert service.update_fcc_base_url("http://127.0.0.1:8082/admin/", user) == (
            "http://127.0.0.1:8082"
        )
        assert service.fcc_base_url() == "http://127.0.0.1:8082"
        assert db.query(AdminSetting).filter_by(key="fcc.base_url").one().value == (
            "http://127.0.0.1:8082"
        )
    finally:
        db.close()
        engine.dispose()


@pytest.mark.asyncio
async def test_fcc_status_reads_local_status_and_models(monkeypatch):
    service = AdminSettingsService(MagicMock())
    service.fcc_base_url = lambda: "http://127.0.0.1:8082"

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, url):
            if url.endswith("/status"):
                return SimpleNamespace(
                    raise_for_status=lambda: None,
                    json=lambda: {
                        "status": "running",
                        "provider": "nvidia_nim",
                        "model": "nvidia/example",
                        "provider_status": [
                            {"provider_id": "nvidia_nim", "status": "connected"},
                            "invalid",
                        ],
                        "startup": {"code": {"state": "ready"}},
                    },
                )
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"models": ["nvidia/example"]},
            )

    monkeypatch.setattr(admin_service.httpx, "AsyncClient", lambda **_kwargs: Client())

    result = await service.fcc_status()

    assert result["connected"]
    assert result["provider"] == "nvidia_nim"
    assert result["active_model"] == "nvidia/example"
    assert result["models"] == ["nvidia/example"]
    assert result["providers"] == [{"provider_id": "nvidia_nim", "status": "connected"}]
    assert result["code_service_status"] == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("failure", "message"),
    [
        ("timeout", "Tempo limite excedido"),
        ("405", "HTTP 405"),
        ("request", "Não foi possível consultar"),
    ],
)
async def test_fcc_status_returns_explicit_connection_failure(monkeypatch, failure, message):
    service = AdminSettingsService(MagicMock())
    service.fcc_base_url = lambda: "http://127.0.0.1:8082"

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, _url):
            if failure == "timeout":
                raise httpx.ReadTimeout("timeout")
            if failure == "request":
                raise httpx.ConnectError("unavailable")
            request = httpx.Request("GET", "http://127.0.0.1:8082/admin/api/status")
            response = httpx.Response(405, request=request)
            raise httpx.HTTPStatusError("method not allowed", request=request, response=response)

    monkeypatch.setattr(admin_service.httpx, "AsyncClient", lambda **_kwargs: Client())

    result = await service.fcc_status()

    assert not result["connected"]
    assert message in result["last_error"]


@pytest.mark.asyncio
async def test_sync_nvidia_key_and_model_to_fcc(monkeypatch):
    user = SimpleNamespace(id=uuid4())
    provider = SimpleNamespace(
        provider_id="nvidia_nim",
        encrypted_api_key="ciphertext",
        model="old-model",
        status="test_pending",
        last_checked_at=None,
        last_error="old error",
        updated_by=None,
    )
    service = AdminSettingsService(MagicMock())
    service.get_provider = lambda _provider_id: provider
    service.fcc_base_url = lambda: "http://127.0.0.1:8082"
    monkeypatch.setattr(admin_service, "_decrypt_credential", lambda _value: "secret-key")
    responses = []

    class Response:
        status_code = 200

        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, _url):
            return Response(
                {
                    "fields": [
                        {
                            "key": "NVIDIA_NIM_API_KEY",
                            "value": {
                                "revision": "revision-1",
                                "entries": [{"reference": 7}, {"reference": "bad"}],
                            },
                        },
                        {"key": "MODEL", "value": "old-model"},
                    ]
                }
            )

        async def post(self, url, json=None):
            responses.append((url, json))
            if url.endswith("/models/refresh"):
                return Response({"models": ["nvidia_nim/example"]})
            return Response({"applied": True})

    monkeypatch.setattr(admin_service.httpx, "AsyncClient", lambda **_kwargs: Client())

    result = await service.sync_nvidia_to_fcc("nvidia_nim/example", user)

    assert result["applied"]
    assert result["catalog_refreshed"]
    assert provider.model == "example"
    assert provider.status == "connected"
    assert provider.last_error is None
    assert provider.updated_by == user.id
    assert responses[0][1]["values"]["NVIDIA_NIM_API_KEY"]["entries"] == [
        {"value": "secret-key"},
        {"retain": 7},
    ]
    assert responses[2][1] == {"values": {"MODEL": "nvidia_nim/example"}}


def test_provider_response_masks_key_and_runtime_apply_filters_keys(monkeypatch):
    monkeypatch.setattr(settings, "credential_encryption_key", Fernet.generate_key().decode())
    encrypted = admin_service._encrypt_credential("abcdefgh-secret")
    provider = AIProviderConfig(
        provider_id="openai-test",
        provider_type="openai",
        name="OpenAI",
        base_url="https://api.openai.com/v1",
        encrypted_api_key=encrypted,
        alternative_models=[],
        available_models=[],
        timeout_seconds=30,
        max_retries=1,
        priority=10,
        is_enabled=True,
        is_default=False,
        status="connected",
        created_by=uuid4(),
        updated_by=uuid4(),
    )

    response = admin_service._provider_response(provider)

    assert response["api_key_configured"]
    assert response["api_key_masked"] == "••••cret"
    assert admin_service._decrypt_credential(encrypted) == "abcdefgh-secret"
    assert admin_service._masked_credential(None) is None
