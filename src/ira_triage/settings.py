from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = Field(min_length=10)
    extraction_model: str = "claude-haiku-4-5-20251001"
    reasoning_model: str = "claude-sonnet-5"

    max_retries: int = 3
    request_timeout_seconds: float = 30.0


class ConfigurationError(RuntimeError):
    """Raised when required configuration is missing or malformed.

    This is a startup problem, not a domain problem: nothing the agent does at
    runtime can recover from it, so it never reaches the model as a tool result.
    """


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        missing = ", ".join(
            str(error["loc"][0]).upper() for error in exc.errors() if error["loc"]
        )
        raise ConfigurationError(
            f"Invalid or missing configuration: {missing}. "
            f"Set it in the environment or copy .env.example to .env and fill it in."
        ) from exc
