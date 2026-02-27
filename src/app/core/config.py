from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    CORS_ORIGINS: str = "http://localhost:5173"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def normalize_cors(cls, v: str) -> str:
        return v.strip()


settings = Settings()