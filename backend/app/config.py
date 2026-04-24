from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/v1"

    DATABASE_URL: str = "postgresql+asyncpg://tfinder:tfinder_dev_password@localhost:5432/tfinder"
    CLOUD_SQL_INSTANCE: Optional[str] = None

    JWT_SECRET_KEY: str = "dev_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FIREBASE_CREDENTIALS_PATH: str = "./firebase-admin-sdk.json"
    FIREBASE_STORAGE_BUCKET: str = "t-finder.appspot.com"

    PASSWORD_ENCRYPTION_KEY: str = ""

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8081"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"


settings = Settings()
