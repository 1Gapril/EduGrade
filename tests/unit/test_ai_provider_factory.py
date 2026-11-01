import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings
from backend.app.core.exceptions import ExternalServiceError
from backend.app.models.admin_settings import AIProviderConfig
from backend.app.services.ai_correction_service import AIProviderFactory, MockProvider


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
