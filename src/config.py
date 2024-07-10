from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


# class LoggingSettings(BaseSettings):
#     """Logging Settings."""
#
#     LEVEL: int
#     FORMAT: str


class PostgresSettings(BaseSettings):
    """PostgreSQL Settings."""

    POSTGRES_HOST: str = Field(default="localhost", max_length=50)
    POSTGRES_PORT: int = Field(default=5432, ge=0, le=5432)
    POSTGRES_DB: str = Field(default="bot", max_length=50)
    DB_USER: str = Field(default="postgres", max_length=50)
    DB_USER_PASS: str = Field(default="1234", max_length=50)



class TgBotSettings(BaseSettings):
    """Telegram Bot Settings."""

    TG_API_TOKEN: str  # TODO: rename to BOT_TOKEN
    ADMINS_ID: list[int] = Field(default_factory=list)
    MESS_MAX_LENGTH: int = Field(default=4096, ge=0, le=4096)


class TgSupportSetting(BaseSettings):
    TG_SUPPORT_BOT_USERNAME: str = Field(
        default="DVRustamov", max_length=50
    )  # TODO: rename to SUPPORT_BOT_USERNAME


class Settings(
    PostgresSettings,
    TgBotSettings,
    TgSupportSetting
):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def asyncpg_db_url(self) -> str:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_USER_PASS,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)

    @property
    def db_url(self) -> str:
        return URL.create(
            drivername="postgresql",
            username=self.DB_USER,
            password=self.DB_USER_PASS,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Get data from .env
settings = get_settings()
