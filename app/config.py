from __future__ import annotations

import os
from pathlib import Path


def _get_env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _normalize_database_url(raw_url: str | None) -> str:
    if not raw_url:
        return "sqlite:///pomodoro.db"
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


def _resolve_local_sqlite_uri(instance_path: str, database_uri: str) -> str:
    if not database_uri.startswith("sqlite:///"):
        return database_uri

    sqlite_target = database_uri.removeprefix("sqlite:///")
    if not sqlite_target or sqlite_target == ":memory:":
        return database_uri

    target_path = Path(sqlite_target)
    if target_path.is_absolute():
        return database_uri

    return f"sqlite:///{(Path(instance_path) / target_path).resolve().as_posix()}"


def _get_test_mode_flag(default: bool = False) -> bool:
    return _get_env_bool("POMODORO_TEST_MODE", default)


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    DEBUG = False
    TESTING = False
    ENV_NAME = "base"

    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Europe/Kyiv")
    POMODORO_TEST_MODE = _get_test_mode_flag(False)
    JSON_SORT_KEYS = False

    API_TITLE = "Pomodoro Work Tracker API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    DEFAULT_WORK_DURATION_MINUTES = 25
    DEFAULT_SHORT_BREAK_MINUTES = 5
    DEFAULT_LONG_BREAK_MINUTES = 25
    DEFAULT_CYCLES_BEFORE_LONG_BREAK = _get_env_int(
        "DEFAULT_CYCLES_BEFORE_LONG_BREAK", 4
    )
    MIN_DURATION_MINUTES = 1
    MAX_WORK_DURATION_MINUTES = 180
    MAX_BREAK_DURATION_MINUTES = 60
    MIN_CYCLES_BEFORE_LONG_BREAK = 2
    MAX_CYCLES_BEFORE_LONG_BREAK = 12

    GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "").strip()
    GOOGLE_CALENDAR_CREDENTIALS_JSON = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS_JSON", ""
    ).strip()
    GOOGLE_CALENDAR_EVENT_PREFIX = os.getenv("GOOGLE_CALENDAR_EVENT_PREFIX", "Pomodoro")
    GOOGLE_CALENDAR_EVENT_COLOR_ID = os.getenv(
        "GOOGLE_CALENDAR_EVENT_COLOR_ID", ""
    ).strip()

    GOOGLE_SHEETS_ENABLED = _get_env_bool("GOOGLE_SHEETS_ENABLED", False)
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "").strip()
    GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv(
        "GOOGLE_SHEETS_CREDENTIALS_JSON", ""
    ).strip()


class DevelopmentConfig(BaseConfig):
    DEBUG = _get_env_bool("DEBUG", True)
    ENV_NAME = "development"


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    ENV_NAME = "testing"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    POMODORO_TEST_MODE = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV_NAME = "production"
    POMODORO_TEST_MODE = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config_class(config_name: str | None) -> type[BaseConfig]:
    resolved_name = (config_name or os.getenv("APP_ENV", "development")).lower()
    return CONFIG_MAP.get(resolved_name, DevelopmentConfig)
