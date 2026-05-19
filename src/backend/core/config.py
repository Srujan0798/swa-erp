from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "swa-erp"
    APP_ENV: str = "dev"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "postgresql://swa:swa@localhost:5432/swa_erp"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MIN: int = 60
    JWT_REFRESH_TTL_DAYS: int = 30


settings = Settings()
