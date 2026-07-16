from __future__ import annotations

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.errors import ValidationAppError
from app.extensions import db
from app.models import UserSettings
from app.repositories import SettingsRepository
from app.time_utils import get_timezone

ALLOWED_THEMES = {"light", "dark", "system"}
ALLOWED_WORK_DURATIONS = {15, 25, 30, 45, 60}
ALLOWED_SHORT_BREAK_DURATIONS = {5, 10, 15}
ALLOWED_LONG_BREAK_DURATIONS = {5, 10, 15, 25}


class SettingsService:
    def __init__(self, repository: SettingsRepository | None = None) -> None:
        self.repository = repository or SettingsRepository()

    def get_settings(self) -> UserSettings:
        settings = self.repository.get_settings()
        if settings is not None:
            return settings

        settings = UserSettings(
            id=1,
            work_duration_minutes=current_app.config["DEFAULT_WORK_DURATION_MINUTES"],
            short_break_minutes=current_app.config["DEFAULT_SHORT_BREAK_MINUTES"],
            long_break_minutes=current_app.config["DEFAULT_LONG_BREAK_MINUTES"],
            cycles_before_long_break=current_app.config[
                "DEFAULT_CYCLES_BEFORE_LONG_BREAK"
            ],
            sound_enabled=True,
            auto_start_next_session=True,
            theme="system",
            timezone=current_app.config["DEFAULT_TIMEZONE"],
        )
        self.repository.save(settings)
        db.session.commit()
        return settings

    def get_settings_payload(self) -> dict[str, object]:
        return self.serialize(self.get_settings())

    def update_settings(self, payload: dict[str, object]) -> dict[str, object]:
        settings = self.get_settings()
        self._validate_payload(payload)

        settings.work_duration_minutes = int(payload["work_duration_minutes"])
        settings.short_break_minutes = int(payload["short_break_minutes"])
        settings.long_break_minutes = int(payload["long_break_minutes"])
        settings.cycles_before_long_break = int(payload["cycles_before_long_break"])
        settings.sound_enabled = bool(payload["sound_enabled"])
        settings.auto_start_next_session = bool(payload["auto_start_next_session"])
        settings.theme = str(payload["theme"])
        settings.timezone = str(payload["timezone"]).strip()

        try:
            self.repository.save(settings)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise ValidationAppError("Unable to save settings") from exc

        return self.serialize(settings)

    def serialize(self, settings: UserSettings) -> dict[str, object]:
        return {
            "work_duration_minutes": settings.work_duration_minutes,
            "short_break_minutes": settings.short_break_minutes,
            "long_break_minutes": settings.long_break_minutes,
            "cycles_before_long_break": settings.cycles_before_long_break,
            "sound_enabled": settings.sound_enabled,
            "auto_start_next_session": settings.auto_start_next_session,
            "theme": settings.theme,
            "timezone": settings.timezone,
            "test_mode_enabled": current_app.config["POMODORO_TEST_MODE"],
        }

    def _validate_payload(self, payload: dict[str, object]) -> None:
        work_duration = int(payload["work_duration_minutes"])
        short_break = int(payload["short_break_minutes"])
        long_break = int(payload["long_break_minutes"])
        cycles_before_long_break = int(payload["cycles_before_long_break"])
        theme = str(payload["theme"])
        timezone_name = str(payload["timezone"]).strip()

        if theme not in ALLOWED_THEMES:
            raise ValidationAppError("Invalid theme", details={"theme": theme})

        get_timezone(timezone_name)

        min_cycles = current_app.config["MIN_CYCLES_BEFORE_LONG_BREAK"]
        max_cycles = current_app.config["MAX_CYCLES_BEFORE_LONG_BREAK"]

        if work_duration not in ALLOWED_WORK_DURATIONS:
            raise ValidationAppError(
                "Invalid work duration",
                details={
                    "work_duration_minutes": work_duration,
                    "allowed_values": sorted(ALLOWED_WORK_DURATIONS),
                },
            )
        if short_break not in ALLOWED_SHORT_BREAK_DURATIONS:
            raise ValidationAppError(
                "Invalid short-break duration",
                details={
                    "short_break_minutes": short_break,
                    "allowed_values": sorted(ALLOWED_SHORT_BREAK_DURATIONS),
                },
            )
        if long_break not in ALLOWED_LONG_BREAK_DURATIONS:
            raise ValidationAppError(
                "Invalid long-break duration",
                details={
                    "long_break_minutes": long_break,
                    "allowed_values": sorted(ALLOWED_LONG_BREAK_DURATIONS),
                },
            )
        if not min_cycles <= cycles_before_long_break <= max_cycles:
            raise ValidationAppError(
                "Invalid long-break interval",
                details={"cycles_before_long_break": cycles_before_long_break},
            )
