"""Administrator settings, provider credentials, and the supported FCC admin API."""

import ipaddress
import socket
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.admin_settings import AdminSetting, AIProviderConfig
from backend.app.models.audit import AuditActionType, AuditLog
from backend.app.models.user import User

PROVIDER_DEFAULTS = {
    "nvidia_nim": ("NVIDIA NIM", "openai", "https://integrate.api.nvidia.com/v1"),
    "openai": ("OpenAI", "openai", "https://api.openai.com/v1"),
    "anthropic": ("Anthropic", "anthropic", "https://api.anthropic.com"),
    "google_gemini": ("Google Gemini", "gemini", "https://generativelanguage.googleapis.com"),
    "deepseek": ("DeepSeek", "openai", "https://api.deepseek.com/v1"),
    "groq": ("Groq", "openai", "https://api.groq.com/openai/v1"),
    "openrouter": ("OpenRouter", "openai", "https://openrouter.ai/api/v1"),
    "ollama": ("Ollama", "ollama", "http://127.0.0.1:11434"),
    "custom": ("Provedor personalizado", "openai", ""),
}
PROVIDER_HOSTS = {
    "nvidia_nim": {"integrate.api.nvidia.com"},
    "openai": {"api.openai.com"},
    "anthropic": {"api.anthropic.com"},
    "google_gemini": {"generativelanguage.googleapis.com"},
    "deepseek": {"api.deepseek.com"},
    "groq": {"api.groq.com"},
    "openrouter": {"openrouter.ai"},
}
RUNTIME_SETTING_KEYS = {
    "max_upload_size_mb",
    "ai_timeout_seconds",
    "ai_max_retries",
    "access_token_expire_minutes",
    "refresh_token_expire_days",
    "tesseract_path",
}


def _now() -> datetime:
    return datetime.now(UTC)


def _credential_cipher() -> Fernet:
    key = settings.credential_encryption_key
    if not key:
        raise HTTPException(
            status_code=503,
            detail=(
                "O cofre de credenciais ainda não foi inicializado. "
                "Configure CREDENTIAL_ENCRYPTION_KEY conforme a documentação."
            ),
        )
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise HTTPException(
            status_code=503,
            detail="CREDENTIAL_ENCRYPTION_KEY é inválida; gere uma chave Fernet válida.",
        ) from exc


def _encrypt_credential(value: str) -> str:
    return _credential_cipher().encrypt(value.encode("utf-8")).decode("ascii")


def _decrypt_credential(value: str) -> str:
    try:
        return _credential_cipher().decrypt(value.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeEncodeError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível descriptografar a credencial; verifique a chave mestra.",
        ) from exc


def _masked_credential(ciphertext: str | None) -> str | None:
    if not ciphertext:
        return None
    return "••••" + _decrypt_credential(ciphertext)[-4:]


def _provider_response(provider: AIProviderConfig) -> dict:
    return {
        "id": provider.id,
        "provider_id": provider.provider_id,
        "provider_type": provider.provider_type,
        "name": provider.name,
        "base_url": provider.base_url,
        "api_key_configured": bool(provider.encrypted_api_key),
        "api_key_masked": _masked_credential(provider.encrypted_api_key),
        "model": provider.model,
        "vision_model": provider.vision_model,
        "alternative_models": provider.alternative_models or [],
        "available_models": provider.available_models or [],
        "timeout_seconds": provider.timeout_seconds,
        "max_retries": provider.max_retries,
        "priority": provider.priority,
        "is_enabled": provider.is_enabled,
        "is_default": provider.is_default,
        "status": provider.status,
        "last_checked_at": provider.last_checked_at,
        "last_error": provider.last_error,
        "updated_at": provider.updated_at,
    }


def _validate_provider_url(provider_type: str, api_style: str, raw_url: str) -> str:
    value = raw_url.strip().rstrip("/")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="URL do provedor inválida.") from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise HTTPException(
            status_code=422,
            detail="Informe uma URL HTTP(S) válida, sem credenciais, query ou fragmento.",
        )
    hostname = parsed.hostname.lower().rstrip(".")

    if api_style == "ollama":
        if parsed.scheme != "http" or hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise HTTPException(
                status_code=422,
                detail="Ollama deve usar HTTP em localhost; endpoints remotos não são permitidos.",
            )
        return value

    allowed_hosts = PROVIDER_HOSTS.get(provider_type)
    if allowed_hosts:
        if parsed.scheme != "https" or hostname not in allowed_hosts:
            raise HTTPException(
                status_code=422,
                detail="O domínio não corresponde ao endpoint oficial deste provedor.",
            )
    elif provider_type == "custom":
        if parsed.scheme != "https":
            raise HTTPException(
                status_code=422,
                detail="Provedores personalizados devem usar HTTPS.",
            )
        try:
            ip = ipaddress.ip_address(hostname)
            if not ip.is_global:
                raise ValueError
            addresses = {item[4][0] for item in socket.getaddrinfo(hostname, port or 443)}
            if not addresses or any(not ipaddress.ip_address(item).is_global for item in addresses):
                raise ValueError
        except (ValueError, OSError) as exc:
            raise HTTPException(
                status_code=422,
                detail="O endpoint personalizado deve resolver somente para IPs públicos.",
            ) from exc
    return value


def _provider_api_style(provider_type: str) -> str:
    return PROVIDER_DEFAULTS[provider_type][1]


def _models_endpoint(provider: AIProviderConfig) -> str:
    base = provider.base_url.rstrip("/")
    if provider.provider_type == "ollama":
        return f"{base}/api/tags"
    if provider.provider_type == "google_gemini":
        return f"{base}/v1beta/models"
    if provider.provider_type == "anthropic":
        return f"{base}/v1/models"
    return f"{base}/models"


def _provider_headers(provider: AIProviderConfig, api_key: str | None) -> dict[str, str]:
    if not api_key:
        return {}
    if provider.provider_type == "anthropic":
        return {"x-api-key": api_key, "anthropic-version": "2023-06-01"}
    if provider.provider_type == "google_gemini":
        return {"x-goog-api-key": api_key}
    return {"Authorization": f"Bearer {api_key}"}


def _extract_models(provider: AIProviderConfig, payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return []
    if provider.provider_type == "ollama":
        records = payload.get("models", [])
        return sorted(
            {
                item["name"]
                for item in records
                if isinstance(item, dict) and isinstance(item.get("name"), str)
            }
        )
    if provider.provider_type == "google_gemini":
        records = payload.get("models", [])
        return sorted(
            {
                item["name"]
                for item in records
                if isinstance(item, dict)
                and isinstance(item.get("name"), str)
                and "generateContent" in item.get("supportedGenerationMethods", [])
            }
        )
    records = payload.get("data", [])
    return sorted(
        {
            item["id"]
            for item in records
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
    )


class AdminSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def _audit(
        self,
        user: User,
        description: str,
        old_values: dict | None,
        new_values: dict | None,
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=user.id,
                action=AuditActionType.CONFIG_CHANGE,
                entity_type="AdminSettings",
                description=description,
                old_values=old_values,
                new_values=new_values,
                success=True,
            )
        )

    def list_providers(self) -> list[dict]:
        rows = self.db.execute(
            select(AIProviderConfig).order_by(
                AIProviderConfig.priority, AIProviderConfig.name
            )
        ).scalars()
        return [_provider_response(row) for row in rows]

    def get_provider(self, provider_id: str) -> AIProviderConfig:
        provider = self.db.execute(
            select(AIProviderConfig).where(AIProviderConfig.provider_id == provider_id)
        ).scalar_one_or_none()
        if provider is None:
            raise HTTPException(status_code=404, detail="Provedor não encontrado.")
        return provider

    def create_provider(self, payload, user: User) -> dict:
        if payload.provider_type not in PROVIDER_DEFAULTS:
            raise HTTPException(status_code=422, detail="Tipo de provedor não suportado.")
        if self.db.execute(
            select(AIProviderConfig.id).where(
                AIProviderConfig.provider_id == payload.provider_id
            )
        ).first():
            raise HTTPException(status_code=409, detail="Identificador de provedor já existe.")
        api_style = _provider_api_style(payload.provider_type)
        base_url = payload.base_url or PROVIDER_DEFAULTS[payload.provider_type][2]
        base_url = _validate_provider_url(payload.provider_type, api_style, base_url)
        key = payload.api_key.get_secret_value().strip() if payload.api_key else None
        if key and not key.strip():
            key = None
        encrypted_key = _encrypt_credential(key) if key else None
        if payload.is_default and (not payload.is_enabled or not payload.model):
            raise HTTPException(
                status_code=422,
                detail="O provedor principal precisa estar ativo e ter um modelo selecionado.",
            )
        if payload.is_default:
            self.db.query(AIProviderConfig).update({"is_default": False})

        provider = AIProviderConfig(
            provider_id=payload.provider_id,
            provider_type=payload.provider_type,
            name=payload.name.strip(),
            base_url=base_url,
            encrypted_api_key=encrypted_key,
            model=payload.model.strip() if payload.model else None,
            vision_model=payload.vision_model.strip() if payload.vision_model else None,
            alternative_models=payload.alternative_models,
            timeout_seconds=payload.timeout_seconds,
            max_retries=payload.max_retries,
            priority=payload.priority,
            is_enabled=payload.is_enabled,
            is_default=payload.is_default,
            status="not_configured" if not encrypted_key and api_style != "ollama" else "test_pending",
            created_by=user.id,
            updated_by=user.id,
        )
        self.db.add(provider)
        self.db.flush()
        self._audit(
            user,
            f"Provedor de IA cadastrado: {provider.provider_id}",
            None,
            self._safe_provider_audit(provider),
        )
        return _provider_response(provider)

    def update_provider(self, provider_id: str, payload, user: User) -> dict:
        provider = self.get_provider(provider_id)
        old_values = self._safe_provider_audit(provider)
        changes = payload.model_dump(exclude_unset=True, exclude={"api_key"})
        provider_type = changes.get("provider_type", provider.provider_type)
        if provider_type not in PROVIDER_DEFAULTS:
            raise HTTPException(status_code=422, detail="Tipo de provedor não suportado.")
        api_style = _provider_api_style(provider_type)
        if "base_url" in changes and changes["base_url"] is not None:
            changes["base_url"] = _validate_provider_url(
                provider_type, api_style, changes["base_url"]
            )
        for field in (
            "provider_type",
            "name",
            "base_url",
            "model",
            "vision_model",
            "alternative_models",
            "timeout_seconds",
            "max_retries",
            "priority",
            "is_enabled",
        ):
            if field in changes:
                value = changes[field]
                if field in {"name", "model", "vision_model"} and isinstance(value, str):
                    value = value.strip() or None
                setattr(provider, field, value)
        if payload.api_key is not None:
            key = payload.api_key.get_secret_value().strip()
            if key:
                provider.encrypted_api_key = _encrypt_credential(key)
                provider.status = "test_pending"
                provider.last_error = None
        if payload.is_default is True:
            if not provider.is_enabled or not provider.model:
                raise HTTPException(
                    status_code=422,
                    detail="O provedor principal precisa estar ativo e ter um modelo selecionado.",
                )
            self.db.query(AIProviderConfig).update({"is_default": False})
            provider.is_default = True
        elif payload.is_default is False:
            provider.is_default = False
        if not provider.is_enabled:
            provider.is_default = False
        provider.updated_by = user.id
        provider.updated_at = _now()
        self.db.flush()
        self._audit(
            user,
            f"Provedor de IA atualizado: {provider.provider_id}",
            old_values,
            self._safe_provider_audit(provider),
        )
        return _provider_response(provider)

    def delete_provider(self, provider_id: str, user: User) -> None:
        provider = self.get_provider(provider_id)
        old_values = self._safe_provider_audit(provider)
        self._audit(
            user,
            f"Provedor de IA removido: {provider.provider_id}",
            old_values,
            None,
        )
        self.db.delete(provider)

    @staticmethod
    def _safe_provider_audit(provider: AIProviderConfig) -> dict:
        return {
            "provider_id": provider.provider_id,
            "provider_type": provider.provider_type,
            "name": provider.name,
            "base_url": provider.base_url,
            "api_key_configured": bool(provider.encrypted_api_key),
            "model": provider.model,
            "vision_model": provider.vision_model,
            "alternative_models": provider.alternative_models,
            "is_enabled": provider.is_enabled,
            "is_default": provider.is_default,
            "priority": provider.priority,
        }

    async def test_provider(self, provider_id: str, user: User) -> dict:
        provider = self.get_provider(provider_id)
        checked_at = _now()
        key = _decrypt_credential(provider.encrypted_api_key) if provider.encrypted_api_key else None
        api_style = _provider_api_style(provider.provider_type)
        if api_style != "ollama" and not key:
            return self._record_provider_test(
                provider,
                user,
                checked_at,
                "not_configured",
                None,
                [],
                "Cadastre uma chave de API para testar este provedor.",
            )
        endpoint = _models_endpoint(provider)
        try:
            async with httpx.AsyncClient(
                timeout=provider.timeout_seconds,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                response = await client.get(
                    endpoint,
                    headers=_provider_headers(provider, key),
                )
            if response.status_code in {401, 403}:
                result = ("authentication_error", response.status_code, [], "A autenticação do provedor foi recusada.")
            elif response.status_code >= 500 or response.status_code in {408, 429}:
                result = ("unavailable", response.status_code, [], f"O provedor respondeu HTTP {response.status_code}.")
            elif not response.is_success:
                result = ("unavailable", response.status_code, [], f"O endpoint de modelos respondeu HTTP {response.status_code}.")
            else:
                try:
                    models = _extract_models(provider, response.json())
                except ValueError:
                    models = []
                result = (
                    "connected",
                    response.status_code,
                    models,
                    "Conexão validada." if models else "Conexão validada; o endpoint não retornou modelos listáveis.",
                )
        except httpx.TimeoutException:
            result = ("unavailable", None, [], "Tempo limite excedido ao consultar o provedor.")
        except httpx.RequestError:
            result = ("unavailable", None, [], "Não foi possível conectar ao endpoint do provedor.")
        return self._record_provider_test(provider, user, checked_at, *result)

    def _record_provider_test(
        self,
        provider: AIProviderConfig,
        user: User,
        checked_at: datetime,
        status: str,
        http_status: int | None,
        models: list[str],
        message: str,
    ) -> dict:
        old_values = {"status": provider.status}
        provider.status = status
        provider.available_models = models
        provider.last_checked_at = checked_at
        provider.last_error = None if status == "connected" else message
        provider.updated_by = user.id
        self._audit(
            user,
            f"Teste de conexão do provedor {provider.provider_id}: {status}",
            old_values,
            {"status": status, "http_status": http_status, "available_models_count": len(models)},
        )
        return {
            "provider_id": provider.provider_id,
            "status": status,
            "http_status": http_status,
            "available_models": models,
            "checked_at": checked_at,
            "message": message,
        }

    def get_runtime_settings(self) -> dict:
        stored = {
            row.key: row.value
            for row in self.db.execute(select(AdminSetting)).scalars()
            if row.key in RUNTIME_SETTING_KEYS
        }
        return {
            key: stored.get(key, getattr(settings, key))
            for key in sorted(RUNTIME_SETTING_KEYS)
        }

    def update_runtime_settings(self, updates: dict, user: User) -> dict:
        old = self.get_runtime_settings()
        for key, value in updates.items():
            setting_row = self.db.get(AdminSetting, key)
            if setting_row is None:
                setting_row = AdminSetting(key=key, value=value, updated_by=user.id)
                self.db.add(setting_row)
            else:
                setting_row.value = value
                setting_row.updated_by = user.id
                setting_row.updated_at = _now()
            setattr(settings, key, value)
        self._audit(
            user,
            "Configurações de sistema atualizadas",
            {key: old[key] for key in updates},
            updates,
        )
        self.db.flush()
        return self.get_runtime_settings()

    def fcc_base_url(self) -> str:
        stored = self.db.get(AdminSetting, "fcc.base_url")
        return stored.value if stored and isinstance(stored.value, str) else settings.fcc_base_url

    def update_fcc_base_url(self, url: str, user: User) -> str:
        base_url = _validate_fcc_url(url)
        row = self.db.get(AdminSetting, "fcc.base_url")
        old_url = row.value if row else settings.fcc_base_url
        if row is None:
            self.db.add(AdminSetting(key="fcc.base_url", value=base_url, updated_by=user.id))
        else:
            row.value = base_url
            row.updated_by = user.id
            row.updated_at = _now()
        self._audit(
            user,
            "Endereço da integração FCC atualizado",
            {"base_url": old_url},
            {"base_url": base_url},
        )
        self.db.flush()
        return base_url

    async def fcc_status(self) -> dict:
        base_url = _validate_fcc_url(self.fcc_base_url())
        checked_at = _now()
        try:
            async with httpx.AsyncClient(
                timeout=5,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                response = await client.get(f"{base_url}/admin/api/status")
                response.raise_for_status()
                status_data = response.json()
                models_response = await client.get(f"{base_url}/admin/api/models")
                models_response.raise_for_status()
                model_data = models_response.json()
            startup = status_data.get("startup", {})
            providers = [
                {"provider_id": item.get("provider_id"), "status": item.get("status")}
                for item in status_data.get("provider_status", [])
                if isinstance(item, dict)
            ]
            return {
                "configured_url": base_url,
                "connected": status_data.get("status") == "running",
                "status": status_data.get("status", "unknown"),
                "version": None,
                "version_available": False,
                "provider": status_data.get("provider"),
                "active_model": status_data.get("model"),
                "providers": providers,
                "models": model_data.get("models", []) if isinstance(model_data, dict) else [],
                "code_service_status": (
                    startup.get("code", {}).get("state")
                    if isinstance(startup.get("code"), dict)
                    else None
                ),
                "last_error": None,
                "checked_at": checked_at,
            }
        except httpx.TimeoutException:
            error = "Tempo limite excedido ao consultar a API administrativa do FCC."
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 405:
                error = (
                    "O FCC respondeu HTTP 405; informe somente a origem local "
                    "(por exemplo, http://127.0.0.1:8082), sem /admin."
                )
            else:
                error = f"API administrativa do FCC respondeu HTTP {exc.response.status_code}."
        except (httpx.RequestError, ValueError):
            error = "Não foi possível consultar a API administrativa do FCC."
        return {
            "configured_url": base_url,
            "connected": False,
            "status": "unavailable",
            "version": None,
            "version_available": False,
            "provider": None,
            "active_model": None,
            "providers": [],
            "models": [],
            "code_service_status": None,
            "last_error": error,
            "checked_at": checked_at,
        }

    async def sync_nvidia_to_fcc(self, model: str, user: User) -> dict:
        provider = self.get_provider("nvidia_nim")
        if not provider.encrypted_api_key:
            raise HTTPException(
                status_code=409,
                detail="Cadastre e teste a chave NVIDIA NIM no EduGrade antes de sincronizar.",
            )
        api_key = _decrypt_credential(provider.encrypted_api_key)
        base_url = _validate_fcc_url(self.fcc_base_url())
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            if not model.startswith("nvidia_nim/"):
                raise HTTPException(
                    status_code=422,
                    detail="Selecione um identificador de modelo NVIDIA NIM.",
                )
            try:
                config_response = await client.get(f"{base_url}/admin/api/config")
                config_response.raise_for_status()
                config_data = config_response.json()
            except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
                raise HTTPException(status_code=502, detail="Não foi possível ler a configuração segura do FCC.") from exc

            fields = {
                item.get("key"): item
                for item in config_data.get("fields", [])
                if isinstance(item, dict)
            }
            credential_field = fields.get("NVIDIA_NIM_API_KEY", {})
            projection = credential_field.get("value", {})
            revision = projection.get("revision") if isinstance(projection, dict) else None
            entries = projection.get("entries", []) if isinstance(projection, dict) else []
            if not isinstance(revision, str) or not isinstance(entries, list):
                raise HTTPException(
                    status_code=502,
                    detail="A API FCC não forneceu os metadados para uma alteração segura das chaves.",
                )
            secret_entries = [{"value": api_key}]
            secret_entries.extend(
                {"retain": item["reference"]}
                for item in entries
                if isinstance(item, dict)
                and type(item.get("reference")) is int
            )
            apply_response = await client.post(
                f"{base_url}/admin/api/config/apply",
                json={
                    "values": {
                        "NVIDIA_NIM_API_KEY": {
                            "revision": revision,
                            "entries": secret_entries,
                        }
                    }
                },
            )
            if apply_response.status_code >= 400:
                raise HTTPException(
                    status_code=502,
                    detail=f"O FCC recusou a atualização da credencial (HTTP {apply_response.status_code}).",
                )
            try:
                apply_data = apply_response.json()
            except ValueError as exc:
                raise HTTPException(status_code=502, detail="O FCC retornou uma resposta inválida.") from exc
            if not apply_data.get("applied"):
                raise HTTPException(
                    status_code=422,
                    detail="O FCC não aplicou a credencial NVIDIA; confira a validação retornada pelo serviço.",
                )

            try:
                refreshed = await client.post(f"{base_url}/admin/api/models/refresh")
                refreshed.raise_for_status()
                refreshed_data = refreshed.json()
            except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
                raise HTTPException(
                    status_code=502,
                    detail="A chave foi aceita pelo FCC, mas a atualização do catálogo falhou.",
                ) from exc
            refreshed_models = refreshed_data.get("models", []) if isinstance(refreshed_data, dict) else []
            if model not in refreshed_models:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "A chave foi salva no FCC, mas o modelo selecionado não apareceu "
                        "no catálogo atualizado. Confirme se o identificador existe no "
                        "catálogo NVIDIA NIM."
                    ),
                )

            current_model = fields.get("MODEL", {}).get("value")
            if not isinstance(current_model, str):
                raise HTTPException(
                    status_code=502,
                    detail="A API FCC não retornou o modelo padrão atual.",
                )
            model_apply = await client.post(
                f"{base_url}/admin/api/config/apply",
                json={"values": {"MODEL": model}},
            )
            if model_apply.status_code >= 400:
                raise HTTPException(
                    status_code=502,
                    detail=f"O FCC recusou a seleção do modelo (HTTP {model_apply.status_code}).",
                )
            try:
                model_result = model_apply.json()
            except ValueError as exc:
                raise HTTPException(status_code=502, detail="O FCC retornou uma resposta inválida ao salvar o modelo.") from exc
            if not model_result.get("applied"):
                raise HTTPException(
                    status_code=422,
                    detail="O FCC não aplicou o modelo selecionado.",
                )

        provider.model = model.removeprefix("nvidia_nim/")
        provider.status = "connected"
        provider.last_checked_at = _now()
        provider.last_error = None
        provider.updated_by = user.id
        self._audit(
            user,
            "Provedor NVIDIA NIM e modelo sincronizados com FCC",
            {"model": current_model},
            {"provider_id": "nvidia_nim", "model": model},
        )
        self.db.flush()
        return {
            "applied": True,
            "provider_id": "nvidia_nim",
            "model": model,
            "catalog_refreshed": True,
            "message": "O FCC aceitou a credencial e o modelo foi localizado e selecionado no catálogo.",
        }

    def overview(self, fcc: dict) -> dict:
        providers = list(self.db.execute(select(AIProviderConfig)).scalars())
        default_provider = next((item.provider_id for item in providers if item.is_default), None)
        try:
            self.db.execute(text("SELECT 1"))
            database_status = "connected"
            dialect = self.db.get_bind().dialect.name
            database_version = None
            if dialect == "sqlite":
                database_version = self.db.execute(text("SELECT sqlite_version()")).scalar_one()
            database_file = self.db.get_bind().url.database if dialect == "sqlite" else None
            size_bytes = Path(database_file).stat().st_size if database_file and Path(database_file).is_file() else None
        except Exception:
            database_status = "error"
            dialect = self.db.get_bind().dialect.name
            database_version = None
            size_bytes = None
        storage_path = Path(settings.upload_dir)
        if not storage_path.is_absolute():
            storage_path = Path.cwd() / storage_path
        try:
            disk = __import__("shutil").disk_usage(storage_path if storage_path.exists() else storage_path.parent)
            free_bytes = disk.free
            storage_status = "available"
        except OSError:
            free_bytes = None
            storage_status = "unavailable"
        return {
            "encryption_key_configured": bool(settings.credential_encryption_key),
            "providers_total": len(providers),
            "providers_enabled": sum(item.is_enabled for item in providers),
            "providers_with_errors": sum(item.status in {"authentication_error", "unavailable"} for item in providers),
            "default_provider": default_provider,
            "database": {
                "status": database_status,
                "type": dialect,
                "version": database_version,
                "size_bytes": size_bytes,
            },
            "storage": {
                "status": storage_status,
                "path": str(storage_path),
                "free_bytes": free_bytes,
            },
            "fcc": fcc,
            "runtime_settings": self.get_runtime_settings(),
        }


def _validate_fcc_url(raw_url: str) -> str:
    value = raw_url.strip().rstrip("/")
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Endereço do FCC inválido.") from exc
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise HTTPException(
            status_code=422,
            detail="Por segurança, a API administrativa FCC só pode ser acessada em localhost.",
        )
    path = parsed.path.rstrip("/")
    if path not in {"", "/admin"}:
        raise HTTPException(
        status_code=422,
        detail="Informe apenas a origem local do FCC, sem caminhos adicionais.",
        )
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


def apply_persisted_runtime_settings(db: Session) -> None:
    for row in db.execute(select(AdminSetting)).scalars():
        if row.key in RUNTIME_SETTING_KEYS:
            setattr(settings, row.key, row.value)
