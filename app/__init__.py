from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import upgrade

from app.api.error_handlers import register_error_handlers
from app.blueprints.calendar.routes import calendar_blp
from app.blueprints.export.routes import export_blp
from app.blueprints.health.routes import health_blp
from app.blueprints.integrations.routes import integrations_blp
from app.blueprints.pages.routes import pages_bp
from app.blueprints.sessions.routes import sessions_blp
from app.blueprints.settings.routes import settings_blp
from app.blueprints.statistics.routes import statistics_blp
from app.commands import register_commands
from app.config import (
    _get_env_bool,
    _get_env_int,
    _get_test_mode_flag,
    _normalize_database_url,
    _resolve_local_sqlite_uri,
    get_config_class,
)
from app.extensions import api, db, migrate
from app.models import user_settings, work_session  # noqa: F401


def create_app(config_name: str | None = None) -> Flask:
    """Створює Flask-застосунок через factory pattern."""

    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(get_config_class(config_name))
    _apply_runtime_environment(app)
    _configure_database_uri(app)

    _configure_logging(app)
    _register_extensions(app)
    _register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)
    _ensure_local_sqlite_ready(app)

    return app


def _configure_logging(app: Flask) -> None:
    if app.logger.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(pages_bp)
    api.register_blueprint(health_blp)
    api.register_blueprint(sessions_blp)
    api.register_blueprint(statistics_blp)
    api.register_blueprint(calendar_blp)
    api.register_blueprint(settings_blp)
    api.register_blueprint(export_blp)
    api.register_blueprint(integrations_blp)


def _apply_runtime_environment(app: Flask) -> None:
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", app.config["SECRET_KEY"])
    app.config["SQLALCHEMY_DATABASE_URI"] = _normalize_database_url(
        os.getenv("DATABASE_URL")
    )
    app.config["DEFAULT_TIMEZONE"] = os.getenv(
        "DEFAULT_TIMEZONE",
        app.config["DEFAULT_TIMEZONE"],
    )
    app.config["POMODORO_TEST_MODE"] = _get_test_mode_flag(
        app.config["POMODORO_TEST_MODE"]
    )
    app.config["DEFAULT_CYCLES_BEFORE_LONG_BREAK"] = _get_env_int(
        "DEFAULT_CYCLES_BEFORE_LONG_BREAK",
        app.config["DEFAULT_CYCLES_BEFORE_LONG_BREAK"],
    )
    app.config["GOOGLE_CALENDAR_ID"] = os.getenv(
        "GOOGLE_CALENDAR_ID",
        app.config["GOOGLE_CALENDAR_ID"],
    ).strip()
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS_JSON",
        app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"],
    ).strip()
    app.config["GOOGLE_CALENDAR_EVENT_PREFIX"] = os.getenv(
        "GOOGLE_CALENDAR_EVENT_PREFIX",
        app.config["GOOGLE_CALENDAR_EVENT_PREFIX"],
    )
    app.config["GOOGLE_CALENDAR_EVENT_COLOR_ID"] = os.getenv(
        "GOOGLE_CALENDAR_EVENT_COLOR_ID",
        app.config["GOOGLE_CALENDAR_EVENT_COLOR_ID"],
    ).strip()

    if app.config["ENV_NAME"] == "development":
        app.config["DEBUG"] = _get_env_bool("DEBUG", app.config["DEBUG"])


def _configure_database_uri(app: Flask) -> None:
    app.config["SQLALCHEMY_DATABASE_URI"] = _resolve_local_sqlite_uri(
        app.instance_path,
        app.config["SQLALCHEMY_DATABASE_URI"],
    )


def _ensure_local_sqlite_ready(app: Flask) -> None:
    database_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if app.config.get("TESTING") or not database_uri.startswith("sqlite:///"):
        return

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    with app.app_context():
        upgrade(directory=str(Path(app.root_path).parent / "migrations"))
        from app.services.settings_service import SettingsService

        SettingsService().get_settings()
