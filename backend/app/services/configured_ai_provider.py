"""Adapters for AI providers configured through the administrator panel."""

import time
from typing import Any
from urllib.parse import quote

import httpx

from backend.app.core.exceptions import ExternalServiceError
from backend.app.schemas.ai_correction import AIHealthCheck


class ConfiguredAIProvider:
    def __init__(
        self,
        *,
        provider_id: str,
        provider_type: str,
        base_url: str,
        api_key: str | None,
        model: str | None,
        vision_model: str | None,
        timeout_seconds: int,
    ):
        self.provider_id = provider_id
        self.provider_type = provider_type
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model or ""
        self.vision_model = vision_model
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout_seconds,
            follow_redirects=False,
            trust_env=False,
            headers=self._headers(),
        )

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        if self.provider_type == "anthropic":
            return {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            }
        if self.provider_type == "google_gemini":
            return {"x-goog-api-key": self.api_key}
        return {"Authorization": f"Bearer {self.api_key}"}

    async def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        try:
            if self.provider_type == "anthropic":
                response = await self.client.post(
                    "/v1/messages",
                    json={
                        "model": model,
                        "max_tokens": kwargs.get("max_tokens", 2048),
                        "temperature": kwargs.get("temperature", 0.1),
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                response.raise_for_status()
                content = response.json().get("content", [])
                return "\n".join(
                    block["text"]
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            if self.provider_type == "google_gemini":
                response = await self.client.post(
                    f"/v1beta/models/{quote(model.removeprefix('models/'), safe='')}:generateContent",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": kwargs.get("temperature", 0.1)},
                    },
                )
                response.raise_for_status()
                return self._gemini_text(response.json())
            if self.provider_type == "ollama":
                response = await self.client.post(
                    "/api/chat",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": {"temperature": kwargs.get("temperature", 0.1)},
                    },
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.1),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("Tempo limite excedido no provedor de IA.") from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                f"O provedor de IA respondeu HTTP {exc.response.status_code}."
            ) from exc
        except (httpx.RequestError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ExternalServiceError("Não foi possível obter uma resposta válida do provedor de IA.") from exc

    async def analyze_image(
        self, image_base64: str, prompt: str, model: str, **kwargs
    ) -> str:
        try:
            if self.provider_type == "anthropic":
                response = await self.client.post(
                    "/v1/messages",
                    json={
                        "model": model,
                        "max_tokens": kwargs.get("max_tokens", 2048),
                        "temperature": kwargs.get("temperature", 0.1),
                        "messages": [{
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": image_base64,
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }],
                    },
                )
                response.raise_for_status()
                return "\n".join(
                    block["text"]
                    for block in response.json().get("content", [])
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            if self.provider_type == "google_gemini":
                response = await self.client.post(
                    f"/v1beta/models/{quote(model.removeprefix('models/'), safe='')}:generateContent",
                    json={
                        "contents": [{
                            "parts": [
                                {"text": prompt},
                                {"inline_data": {"mime_type": "image/png", "data": image_base64}},
                            ],
                        }],
                    },
                )
                response.raise_for_status()
                return self._gemini_text(response.json())
            if self.provider_type == "ollama":
                response = await self.client.post(
                    "/api/chat",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt, "images": [image_base64]}],
                        "stream": False,
                    },
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                            },
                        ],
                    }],
                    "temperature": kwargs.get("temperature", 0.1),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("Tempo limite excedido no provedor de IA.") from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                f"O provedor de IA respondeu HTTP {exc.response.status_code}."
            ) from exc
        except (httpx.RequestError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ExternalServiceError("Não foi possível analisar a imagem no provedor de IA.") from exc

    async def analyze_document(self, file_path: str, prompt: str, model: str, **kwargs) -> str:
        return await self.generate_text(prompt, model, **kwargs)

    async def health_check(self) -> AIHealthCheck:
        started = time.monotonic()
        try:
            models = await self.get_available_models()
            return AIHealthCheck(
                provider=self.provider_id,
                status="healthy" if models else "unhealthy",
                model=self.model,
                latency_ms=int((time.monotonic() - started) * 1000),
                error=None if models else "O endpoint não retornou modelos disponíveis.",
            )
        except ExternalServiceError as exc:
            return AIHealthCheck(
                provider=self.provider_id,
                status="unhealthy",
                model=self.model,
                latency_ms=int((time.monotonic() - started) * 1000),
                error=exc.message,
            )

    async def get_available_models(self) -> list[str]:
        if self.provider_type == "ollama":
            endpoint = "/api/tags"
        elif self.provider_type == "google_gemini":
            endpoint = "/v1beta/models"
        elif self.provider_type == "anthropic":
            endpoint = "/v1/models"
        else:
            endpoint = "/models"
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            if self.provider_type == "ollama":
                return sorted(item["name"] for item in data.get("models", []) if "name" in item)
            if self.provider_type == "google_gemini":
                return sorted(
                    item["name"]
                    for item in data.get("models", [])
                    if "name" in item
                    and "generateContent" in item.get("supportedGenerationMethods", [])
                )
            return sorted(item["id"] for item in data.get("data", []) if "id" in item)
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("Tempo limite excedido ao consultar modelos.") from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                f"O provedor respondeu HTTP {exc.response.status_code} ao consultar modelos."
            ) from exc
        except (httpx.RequestError, KeyError, TypeError, ValueError) as exc:
            raise ExternalServiceError("Não foi possível consultar modelos do provedor.") from exc

    @staticmethod
    def _gemini_text(data: dict[str, Any]) -> str:
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("Resposta Gemini sem candidatos.")
        parts = candidates[0].get("content", {}).get("parts", [])
        return "\n".join(part["text"] for part in parts if isinstance(part, dict) and "text" in part)

    async def close(self) -> None:
        await self.client.aclose()
