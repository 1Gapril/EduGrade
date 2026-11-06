"""Request and response models for administrator settings."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

ProviderType = Literal[
    "nvidia_nim",
    "openai",
    "anthropic",
    "google_gemini",
    "deepseek",
    "groq",
    "openrouter",
    "ollama",
    "custom",
]


class AIProviderConfigCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: str = Field(pattern=r"^[a-z][a-z0-9_-]{1,79}$")
    provider_type: ProviderType
    name: str = Field(min_length=2, max_length=120)
    base_url: str = Field(min_length=8, max_length=500)
    api_key: SecretStr | None = None
    model: str | None = Field(None, max_length=255)
    vision_model: str | None = Field(None, max_length=255)
    alternative_models: list[str] = Field(default_factory=list, max_length=10)
    timeout_seconds: int = Field(default=60, ge=1, le=600)
    max_retries: int = Field(default=2, ge=0, le=10)
    priority: int = Field(default=100, ge=1, le=10000)
    is_enabled: bool = False
    is_default: bool = False

    @field_validator("alternative_models")
    @classmethod
    def normalize_alternative_models(cls, values: list[str]) -> list[str]:
        normalized = [value.strip() for value in values if value.strip()]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Os modelos alternativos não podem se repetir.")
        return normalized


class AIProviderConfigUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_type: ProviderType | None = None
    name: str | None = Field(None, min_length=2, max_length=120)
    base_url: str | None = Field(None, min_length=8, max_length=500)
    api_key: SecretStr | None = None
    model: str | None = Field(None, max_length=255)
    vision_model: str | None = Field(None, max_length=255)
    alternative_models: list[str] | None = Field(None, max_length=10)
    timeout_seconds: int | None = Field(None, ge=1, le=600)
    max_retries: int | None = Field(None, ge=0, le=10)
    priority: int | None = Field(None, ge=1, le=10000)
    is_enabled: bool | None = None
    is_default: bool | None = None


class AIProviderConfigResponse(BaseModel):
    id: UUID
    provider_id: str
    provider_type: str
    name: str
    base_url: str
    api_key_configured: bool
    api_key_masked: str | None
    model: str | None
    vision_model: str | None
    alternative_models: list[str]
    available_models: list[str]
    timeout_seconds: int
    max_retries: int
    priority: int
    is_enabled: bool
    is_default: bool
    status: str
    last_checked_at: datetime | None
    last_error: str | None
    updated_at: datetime


class ProviderTestResponse(BaseModel):
    provider_id: str
    status: str
    http_status: int | None = None
    available_models: list[str] = Field(default_factory=list)
    checked_at: datetime
    message: str


class SystemSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_upload_size_mb: int | None = Field(None, ge=1, le=500)
    ai_timeout_seconds: int | None = Field(None, ge=1, le=600)
    ai_max_retries: int | None = Field(None, ge=0, le=10)
    access_token_expire_minutes: int | None = Field(None, ge=5, le=1440)
    refresh_token_expire_days: int | None = Field(None, ge=1, le=90)
    tesseract_path: str | None = Field(None, min_length=1, max_length=500)


class FccSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_url: str = Field(min_length=8, max_length=255)


class FccNvidiaSyncRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(min_length=3, max_length=255)


class FccStatusResponse(BaseModel):
    configured_url: str
    connected: bool
    status: str
    version: str | None = None
    version_available: bool
    provider: str | None = None
    active_model: str | None = None
    providers: list[dict]
    models: list[str]
    code_service_status: str | None = None
    last_error: str | None = None
    checked_at: datetime


class AdminSettingsOverview(BaseModel):
    encryption_key_configured: bool
    providers_total: int
    providers_enabled: int
    providers_with_errors: int
    default_provider: str | None
    database: dict
    storage: dict
    fcc: FccStatusResponse
    runtime_settings: dict


class AdminSettingAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str
    old_values: dict | None
    new_values: dict | None
    success: bool
    created_at: datetime


class StorageFolderUsage(BaseModel):
    """Uso de disco de uma pasta de armazenamento."""

    key: str
    label: str
    path: str
    exists: bool
    file_count: int
    total_bytes: int


class StorageUsageResponse(BaseModel):
    """Resumo do armazenamento local do EduGrade."""

    folders: list[StorageFolderUsage]
    database_path: str | None = None
    database_bytes: int = 0
    total_bytes: int = 0
    free_bytes: int | None = None
    generated_at: datetime
