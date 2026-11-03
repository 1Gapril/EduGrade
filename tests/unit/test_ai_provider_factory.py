import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings
from backend.app.core.exceptions import ExternalServiceError
from backend.app.models.admin_settings import AIProviderConfig
from backend.app.services.ai_correction_service import (
    AIProviderFactory,
    MockProvider,
)
from backend.app.services.configured_ai_provider import ConfiguredAIProvider


@pytest.mark.parametrize("provider_type", ["openai", "anthropic"])
def test_unimplemented_configured_provider_fails_without_mock_fallback(
    provider_type,
    monkeypatch,
):
    engine = create_engine("sqlite://")
    AIProviderConfig.__table__.create(engine)
    test_session = sessionmaker(bind=engine)
    db = test_session()
    monkeypatch.setattr(settings, "ai_provider", provider_type)
    monkeypatch.setattr(AIProviderFactory, "_providers", {provider_type: MockProvider()})

    try:
        with pytest.raises(ExternalServiceError, match="ainda não é suportado"):
            AIProviderFactory.get_provider(db=db)
    finally:
        db.close()
        engine.dispose()


async def test_fcc_claude_is_used_instead_of_admin_default(monkeypatch):
    monkeypatch.setattr(AIProviderFactory, "_providers", {})
    monkeypatch.setattr(settings, "ai_provider", "mock")
    monkeypatch.setattr(settings, "fcc_base_url", "http://127.0.0.1:8082")
    monkeypatch.setattr(settings, "fcc_model", "claude-sonnet-4-20250514")

    class UnexpectedAdminDefault:
        def execute(self, *_args, **_kwargs):
            raise AssertionError("FCC selection must bypass the database provider.")

    provider = None
    try:
        provider = AIProviderFactory.get_provider(
            provider_type="fcc_claude",
            db=UnexpectedAdminDefault(),
        )
        assert isinstance(provider, ConfiguredAIProvider)
        assert provider.provider_id == "fcc_claude"
        assert provider.provider_type == "anthropic"
        assert provider.base_url == "http://127.0.0.1:8082"
        assert provider.api_key is None
        assert provider.model == "claude-sonnet-4-20250514"
        assert provider.client.headers["anthropic-version"] == "2023-06-01"
    finally:
        if provider is not None:
            await provider.close()
