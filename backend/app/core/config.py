"""Configurações da aplicação EduGrade."""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    # Application
    app_name: str = "EduGrade"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./edugrade.db"

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production-min-32-chars-long",
        description="Chave secreta para JWT (mínimo 32 caracteres em produção)"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_hash_algorithm: str = "argon2"

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
    )

    # File Upload
    max_upload_size_mb: int = 50
    upload_dir: str = "./storage/exams"
    material_storage_dir: str = "./storage/materials"
    processed_dir: str = "./storage/processed"
    temp_dir: str = "./storage/temp"
    allowed_extensions: List[str] = Field(default=[".pdf", ".jpg", ".jpeg", ".png"])

    # AI Providers
    ai_provider: str = "mock"  # mock, ollama, openai, anthropic
    ollama_base_url: str = "http://localhost:11434"
    ollama_text_model: str = "llama3.1"
    ollama_multimodal_model: str = "llava"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_timeout_seconds: int = 120
    ai_max_retries: int = 3
    credential_encryption_key: Optional[str] = None
    fcc_base_url: str = "http://127.0.0.1:8082"

    # OCR
    ocr_engine: str = "tesseract"  # tesseract, paddleocr
    tesseract_path: str = "tesseract"
    paddleocr_lang: str = "pt"

    # Email (optional)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "noreply@edugrade.local"

    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/edugrade.log"

    # Backup
    backup_dir: str = "./storage/backups"
    backup_retention_days: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()


settings = get_settings()