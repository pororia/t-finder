from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/v1"

    DATABASE_URL: str = "postgresql+asyncpg://tfinder:tfinder_dev_password@localhost:5432/tfinder"
    # Cloud Run에서 Cloud SQL 연결 시 설정 (예: project:region:instance)
    # 설정되면 DATABASE_URL의 host 대신 Unix 소켓으로 연결
    CLOUD_SQL_INSTANCE: Optional[str] = None

    JWT_SECRET_KEY: str = "dev_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FIREBASE_CREDENTIALS_PATH: str = "./firebase-admin-sdk.json"
    FIREBASE_STORAGE_BUCKET: str = "t-finder.appspot.com"

    PASSWORD_ENCRYPTION_KEY: str = ""

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8081"]

    class Config:
        env_file = ".env"


settings = Settings()
