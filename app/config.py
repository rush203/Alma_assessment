
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyUrl

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")
    APP_NAME: str = "Lead Intake Service"
    ENV: str = "dev"

    SECRET_KEY: str = "devsecretkeychangeit"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BASE_URL: str = "http://localhost:8000"

    DATABASE_URL: str = "sqlite:///./app.db"

    MAILER_BACKEND: str = "console"  # "smtp" or "console"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = False
    FROM_EMAIL: str = "Acme Law <no-reply@acmelaw.test>"
    ATTORNEY_EMAIL: str = "attorney@example.com"

    UPLOAD_DIR: str = "./uploads"
    OUTBOX_DIR: str = "./outbox"

settings = Settings()
