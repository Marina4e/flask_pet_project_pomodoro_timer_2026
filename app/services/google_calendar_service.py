from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.errors import ConflictAppError, ValidationAppError
from app.extensions import db
from app.repositories import SessionRepository
from app.services.settings_service import SettingsService
from app.time_utils import to_local_datetime


class GoogleCalendarService:
    CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.events"
    GOOGLE_CALENDAR_EMBED_HOSTS = {"calendar.google.com", "www.google.com"}
    REQUIRED_CREDENTIAL_FIELDS = (
        "type",
        "client_email",
        "private_key",
        "token_uri",
    )

    def __init__(
        self,
        repository: SessionRepository | None = None,
        settings_service: SettingsService | None = None,
    ) -> None:
        self.repository = repository or SessionRepository()
        self.settings_service = settings_service or SettingsService()

    def get_status(self) -> dict[str, object]:
        configured_calendar_id = current_app.config["GOOGLE_CALENDAR_ID"] or None
        normalized_calendar_id = self._normalize_calendar_id(configured_calendar_id)
        credentials_json = current_app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"]
        missing: list[str] = []

        if not configured_calendar_id:
            missing.append("GOOGLE_CALENDAR_ID")
        if not credentials_json:
            missing.append("GOOGLE_CALENDAR_CREDENTIALS_JSON")

        calendar_id_valid = normalized_calendar_id is not None
        latest_work_session = self.repository.get_latest_work_session()

        return {
            "configured": not missing and calendar_id_valid,
            "calendar_id": normalized_calendar_id or configured_calendar_id,
            "calendar_id_valid": calendar_id_valid,
            "calendar_id_normalized": bool(
                normalized_calendar_id
                and configured_calendar_id
                and normalized_calendar_id != configured_calendar_id.strip()
            ),
            "missing": missing,
            "latest_work_session_id": (
                latest_work_session.id if latest_work_session is not None else None
            ),
            "latest_work_session_synced": bool(
                latest_work_session and latest_work_session.google_calendar_event_id
            ),
        }

    def sync_latest_work_session(
        self, timezone_name: str | None = None
    ) -> dict[str, object]:
        status = self.get_status()
        if status["calendar_id"] and not status["calendar_id_valid"]:
            raise ValidationAppError(
                "Google Calendar ID is invalid. Use the Calendar ID or an official "
                "Google Calendar embed URL containing src=."
            )
        if not status["configured"]:
            raise ValidationAppError(
                "Google Calendar integration is not configured",
                details={"missing": status["missing"]},
            )

        session = self.repository.get_latest_work_session()
        if session is None:
            raise ValidationAppError("No completed work session is available to sync")

        if session.google_calendar_event_id:
            raise ConflictAppError(
                "Latest completed work session is already synced",
                details={
                    "session_id": session.id,
                    "sync_status": "already_synced",
                },
            )

        resolved_timezone = (
            timezone_name or self.settings_service.get_settings().timezone
        )
        service = self._build_calendar_service()
        event_payload = self._build_event_payload(session, resolved_timezone)

        try:
            response = (
                service.events()
                .insert(
                    calendarId=status["calendar_id"],
                    body=event_payload,
                )
                .execute()
            )
            session.google_calendar_event_id = str(response["id"])
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            current_app.logger.error(
                "Google Calendar event could not be stored for session %s (%s)",
                session.id,
                type(exc).__name__,
            )
            raise ValidationAppError(
                "Calendar event was created but could not be stored locally"
            ) from exc
        except Exception as exc:  # pragma: no cover - external API wrapper
            current_app.logger.error(
                "Google Calendar sync failed for session %s (%s)",
                session.id,
                type(exc).__name__,
            )
            raise ValidationAppError(
                "Failed to create Google Calendar event. Check the Calendar ID, "
                "API access, credentials, and sharing permissions."
            ) from exc

        return {
            "status": self.get_status(),
            "timezone": resolved_timezone,
            "session_id": session.id,
            "event_id": session.google_calendar_event_id,
            "html_link": response.get("htmlLink"),
        }

    def _build_event_payload(self, session, timezone_name: str) -> dict[str, object]:
        start_local = to_local_datetime(session.started_at_utc, timezone_name)
        end_local = to_local_datetime(session.completed_at_utc, timezone_name)
        duration_minutes = round(session.actual_duration_seconds / 60, 2)
        summary_prefix = current_app.config["GOOGLE_CALENDAR_EVENT_PREFIX"]

        payload: dict[str, object] = {
            "summary": f"{summary_prefix} focus session",
            "description": (
                f"Pomodoro Work Tracker session #{session.id}\n"
                f"client_session_id: {session.client_session_id}\n"
                f"Duration (minutes): {duration_minutes}"
            ),
            "start": {
                "dateTime": start_local.isoformat(),
                "timeZone": timezone_name,
            },
            "end": {
                "dateTime": end_local.isoformat(),
                "timeZone": timezone_name,
            },
        }

        color_id = current_app.config["GOOGLE_CALENDAR_EVENT_COLOR_ID"]
        if color_id:
            payload["colorId"] = color_id

        return payload

    @classmethod
    def _build_calendar_service(cls):
        credentials_json = current_app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"]
        if not credentials_json:
            raise ValidationAppError("Google Calendar credentials are missing")

        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise ValidationAppError(
                "Google Calendar dependencies are missing. "
                "Run pip install -r requirements.txt."
            ) from exc

        try:
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError as exc:
            raise ValidationAppError(
                "GOOGLE_CALENDAR_CREDENTIALS_JSON is not valid JSON"
            ) from exc

        missing_fields = cls._missing_credential_fields(credentials_info)
        if missing_fields:
            raise ValidationAppError(
                "Google Calendar credentials are invalid or incomplete",
                details={"missing_fields": missing_fields},
            )

        try:
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=[cls.CALENDAR_SCOPE],
            )
            return build(
                "calendar",
                "v3",
                credentials=credentials,
                cache_discovery=False,
            )
        except Exception as exc:  # pragma: no cover - dependency wrapper
            current_app.logger.error(
                "Google Calendar client initialization failed (%s)",
                type(exc).__name__,
            )
            raise ValidationAppError(
                "Google Calendar credentials are invalid or incomplete"
            ) from exc

    @classmethod
    def _missing_credential_fields(cls, credentials_info: object) -> list[str]:
        if not isinstance(credentials_info, dict):
            return list(cls.REQUIRED_CREDENTIAL_FIELDS)

        missing = [
            field
            for field in cls.REQUIRED_CREDENTIAL_FIELDS
            if not str(credentials_info.get(field, "")).strip()
        ]
        if credentials_info.get("type") != "service_account" and "type" not in missing:
            missing.append("type")
        return missing

    @classmethod
    def _is_calendar_id_valid(cls, calendar_id: object) -> bool:
        return cls._normalize_calendar_id(calendar_id) is not None

    @classmethod
    def _normalize_calendar_id(cls, calendar_id: object) -> str | None:
        if not isinstance(calendar_id, str) or not calendar_id.strip():
            return None

        value = calendar_id.strip()
        if "://" not in value:
            if any(character.isspace() for character in value):
                return None
            return value

        parsed = urlparse(value)
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or (parsed.hostname or "").lower() not in cls.GOOGLE_CALENDAR_EMBED_HOSTS
        ):
            return None

        for source in parse_qs(parsed.query).get("src", []):
            normalized_source = source.strip()
            if normalized_source and not any(
                character.isspace() for character in normalized_source
            ):
                return normalized_source
        return None
