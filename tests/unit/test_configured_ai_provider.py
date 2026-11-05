import httpx
import pytest

from backend.app.core.exceptions import ExternalServiceError
from backend.app.services.configured_ai_provider import ConfiguredAIProvider


async def _provider(provider_type, handler):
    provider = ConfiguredAIProvider(
        provider_id="test-provider",
        provider_type=provider_type,
        base_url="https://provider.example.test",
        api_key="unit-test-key",
        model="text-model",
        vision_model="vision-model",
        timeout_seconds=5,
    )
    await provider.close()
    provider.client = httpx.AsyncClient(
        base_url=provider.base_url,
        headers=provider._headers(),
        transport=httpx.MockTransport(handler),
        follow_redirects=False,
        trust_env=False,
    )
    return provider


@pytest.mark.parametrize(
    ("provider_type", "path", "response"),
    [
        (
            "anthropic",
            "/v1/messages",
            {"content": [{"type": "text", "text": "generated"}]},
        ),
        (
            "google_gemini",
            "/v1beta/models/text-model:generateContent",
            {"candidates": [{"content": {"parts": [{"text": "generated"}]}}]},
        ),
        ("ollama", "/api/chat", {"message": {"content": "generated"}}),
        (
            "openai",
            "/chat/completions",
            {"choices": [{"message": {"content": "generated"}}]},
        ),
    ],
)
@pytest.mark.asyncio
async def test_generate_text_uses_provider_endpoint_and_response_shape(
    provider_type, path, response
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=response)

    provider = await _provider(provider_type, handler)
    try:
        assert await provider.generate_text("prompt", "text-model") == "generated"
    finally:
        await provider.close()

    assert requests[0].url.path == path
    assert "prompt" in requests[0].content.decode()


@pytest.mark.parametrize(
    ("provider_type", "expected_header"),
    [
        ("openai", ("authorization", "Bearer unit-test-key")),
        ("google_gemini", ("x-goog-api-key", "unit-test-key")),
        ("anthropic", ("x-api-key", "unit-test-key")),
    ],
)
@pytest.mark.asyncio
async def test_provider_sends_configured_authentication_header(provider_type, expected_header):
    provider = await _provider(
        provider_type,
        lambda request: httpx.Response(200, json={"data": []}),
    )
    try:
        headers = provider.client.headers
        assert headers[expected_header[0]] == expected_header[1]
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_generate_text_surfaces_provider_http_errors():
    provider = await _provider(
        "openai",
        lambda _request: httpx.Response(401, json={"error": "unauthorized"}),
    )
    try:
        with pytest.raises(ExternalServiceError, match="HTTP 401"):
            await provider.generate_text("prompt", "text-model")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_generate_text_surfaces_provider_timeouts():
    def timeout(_request):
        raise httpx.ReadTimeout("request timed out")

    provider = await _provider("openai", timeout)
    try:
        with pytest.raises(ExternalServiceError, match="Tempo limite"):
            await provider.generate_text("prompt", "text-model")
    finally:
        await provider.close()


@pytest.mark.parametrize(
    ("provider_type", "response"),
    [
        (
            "anthropic",
            {"content": [{"type": "text", "text": "vision result"}]},
        ),
        (
            "google_gemini",
            {"candidates": [{"content": {"parts": [{"text": "vision result"}]}}]},
        ),
        ("ollama", {"message": {"content": "vision result"}}),
        (
            "openai",
            {"choices": [{"message": {"content": "vision result"}}]},
        ),
    ],
)
@pytest.mark.asyncio
async def test_analyze_image_uses_supported_provider_response(provider_type, response):
    provider = await _provider(
        provider_type,
        lambda _request: httpx.Response(200, json=response),
    )
    try:
        result = await provider.analyze_image("image-data", "describe", "vision-model")
    finally:
        await provider.close()

    assert result == "vision result"


@pytest.mark.asyncio
async def test_health_check_reports_available_models():
    provider = await _provider(
        "openai",
        lambda _request: httpx.Response(
            200,
            json={"data": [{"id": "model-a"}, {"id": "model-b"}]},
        ),
    )
    try:
        health = await provider.health_check()
    finally:
        await provider.close()

    assert health.status == "healthy"
    assert health.provider == "test-provider"
    assert health.error is None
