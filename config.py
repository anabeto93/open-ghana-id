from __future__ import annotations

import logging
import logging.config
import uuid
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Open Ghana ID"
    debug: bool = False
    sentry_dsn: str | None = None
    cors_allow_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_prefix="OPEN_GHANA_ID_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": (
                "%(levelprefix)s | %(asctime)s | %(request_id)s | "
                "%(pathname)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "open-ghana-id": {"handlers": ["default"], "level": "INFO"},
    },
}


logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("open-ghana-id")


def get_logger() -> logging.LoggerAdapter:
    request_id = str(uuid.uuid4())[:8]
    return logging.LoggerAdapter(_logger, {"request_id": request_id})
