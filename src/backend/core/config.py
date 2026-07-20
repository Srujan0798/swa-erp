from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "change-me"
INSECURE_SECRET_KEYS = {"change-me", "replace-with-openssl-rand-hex-32", ""}


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

    AUTH_RATE_LIMIT_PER_MIN: int = 5

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        if self.APP_ENV.lower() != "dev" and self.SECRET_KEY in INSECURE_SECRET_KEYS:
            raise ValueError(
                "SECRET_KEY is set to an insecure default value but APP_ENV is "
                f"'{self.APP_ENV}'. Refusing to start. Generate a strong secret with: "
                "python3 -c \"import secrets; print(secrets.token_hex(32))\" "
                "and set it in the environment or .env file."
            )
        return self


settings = Settings()
