from __future__ import annotations

import click
from flask import Flask

from app.services.settings_service import SettingsService


def register_commands(app: Flask) -> None:
    @app.cli.command("seed-settings")
    def seed_settings() -> None:
        """Створює запис налаштувань за замовчуванням."""

        settings = SettingsService().get_settings()
        click.echo(
            f"Settings ready: theme={settings.theme}, timezone={settings.timezone}"
        )
