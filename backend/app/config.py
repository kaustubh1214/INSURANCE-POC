"""
Application configuration using pydantic-settings.
All settings are loaded from environment variables / .env file.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings class.
    Values are read from environment variables (case-insensitive).
    Falls back to .env file if variable not set.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "InsureBridge"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./insurebridge.db"

    # --- Security ---
    jwt_secret_key: str = "INSECURE_DEFAULT_CHANGE_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- CORS ---
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    # --- File Storage ---
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    allowed_file_types: str = "pdf,jpg,jpeg,png,tiff"

    @property
    def allowed_extensions(self) -> List[str]:
        return [e.strip().lower() for e in self.allowed_file_types.split(",")]

    # --- AI Services ---
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ai_model: str = "gpt-4o"
    ai_temperature: float = 0.1
    ai_max_tokens: int = 2000

    # --- OCR ---
    tesseract_cmd: str = "/usr/bin/tesseract"

    # --- Vector Store ---
    chroma_db_path: str = "./chroma_db"

    # --- Admin Seed ---
    admin_email: str = "admin@insurebridge.com"
    admin_password: str = "Admin@123456"
    admin_name: str = "System Admin"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Use this as a FastAPI dependency: settings = Depends(get_settings)
    """
    return Settings()


# Module-level singleton for non-dependency use
settings = get_settings()
