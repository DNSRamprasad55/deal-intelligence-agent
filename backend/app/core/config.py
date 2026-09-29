from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Deal Intelligence Agent"
    VERSION: str = "0.2.0"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./deal_intelligence.db"

    # Hindsight Cloud Memory System
    HINDSIGHT_API_KEY: Optional[str] = None
    HINDSIGHT_BASE_URL: str = "https://api.hindsight.vectorize.io"
    HINDSIGHT_BANK_ID: str = "deal-intelligence-global"

    # Backward compatibility alias
    HINDSIGHT_API_URL: Optional[str] = None

    # LLM Provider
    LLM_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"

    # Authentication & Security
    JWT_SECRET: str = "super_secret_jwt_key_change_me_in_production_32_bytes_min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_hindsight_base_url(self) -> str:
        return self.HINDSIGHT_BASE_URL or self.HINDSIGHT_API_URL or "https://api.hindsight.vectorize.io"


settings = Settings()
