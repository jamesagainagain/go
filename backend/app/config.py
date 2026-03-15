from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_db_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_DB_URL"),
    )
    database_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("REDIS_URL"),
    )
    secret_key: str = Field(
        default="change-me-in-production",
        validation_alias=AliasChoices("SECRET_KEY"),
    )
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY"),
    )
    openai_model: str = Field(
        default="gpt-4o",
        validation_alias=AliasChoices("OPENAI_MODEL"),
    )
    openai_model_fast: str = Field(
        default="gpt-4o-mini",
        validation_alias=AliasChoices("OPENAI_MODEL_FAST"),
    )
    mapbox_access_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MAPBOX_ACCESS_TOKEN"),
    )
    mapbox_style: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MAPBOX_STYLE"),
    )
    enable_places_catalog_ingestion: bool = Field(
        default=True,
        validation_alias=AliasChoices("ENABLE_PLACES_CATALOG_INGESTION"),
    )
    openclaw_enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("OPENCLAW_ENABLED"),
    )
    openclaw_endpoint: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENCLAW_ENDPOINT"),
    )
    openclaw_api_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENCLAW_API_TOKEN"),
    )
    openclaw_timeout_seconds: float = Field(
        default=4.0,
        validation_alias=AliasChoices("OPENCLAW_TIMEOUT_SECONDS"),
    )
    vapid_public_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("VAPID_PUBLIC_KEY"),
    )
    vapid_private_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("VAPID_PRIVATE_KEY"),
    )
    vapid_contact_email: str | None = Field(
        default=None,
        validation_alias=AliasChoices("VAPID_CONTACT_EMAIL"),
    )
    activation_check_interval_minutes: int = Field(
        default=15,
        validation_alias=AliasChoices("ACTIVATION_CHECK_INTERVAL_MINUTES"),
    )
    max_opportunities_per_activation: int = Field(
        default=3,
        validation_alias=AliasChoices("MAX_OPPORTUNITIES_PER_ACTIVATION"),
    )
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL"))
    calendar_webhook_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CALENDAR_WEBHOOK_SECRET"),
    )

    @property
    def effective_database_url(self) -> str:
        if self.supabase_db_url:
            return self.supabase_db_url
        if self.database_url:
            return self.database_url
        raise ValueError("Set SUPABASE_DB_URL or DATABASE_URL.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
