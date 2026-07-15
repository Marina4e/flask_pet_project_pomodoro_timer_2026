from __future__ import annotations

import json
import re

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.errors import ValidationAppError
from app.extensions import db
from app.repositories import SessionRepository
from app.services.settings_service import SettingsService
from app.time_utils import to_local_datetime


class GoogleSheetsService:
    SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"
    SHEET_RANGE = "A:I"
    HEADER_RANGE = "A1:I1"
    HEADERS = [
        "Session ID",
        "Date",
        "Start Time",
        "End Time",
        "Planned Duration",
        "Actual Duration",
        "Mode",
        "Timezone",
        "Created At",
    ]
    SPREADSHEET_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{20,200}$")

    def __init__(
        self,
        repository: SessionRepository | None = None,
        settings_service: SettingsService | None = None,
    ) -> None:
        self.repository = repository or SessionRepository()
        self.settings_service = settings_service or SettingsService()

    def get_settings_payload(self) -> dict[str, object]:
        settings = self.settings_service.get_settings()
        enabled = settings.google_sheets_enabled
        spreadsheet_id = settings.google_sheets_spreadsheet_id

        if enabled is None:
            enabled = current_app.config["GOOGLE_SHEETS_ENABLED"]
        if spreadsheet_id is None:
            spreadsheet_id = current_app.config["GOOGLE_SHEETS_SPREADSHEET_ID"]

        return {
            "enabled": bool(enabled),
            "spreadsheet_id": spreadsheet_id or "",
            "credentials_configured": bool(
                current_app.config["GOOGLE_SHEETS_CREDENTIALS_JSON"]
            ),
        }

    def update_settings(self, payload: dict[str, object]) -> dict[str, object]:
        enabled = bool(payload["enabled"])
        spreadsheet_id = str(payload["spreadsheet_id"]).strip()
        self._validate_spreadsheet_id(spreadsheet_id)

        if enabled and not spreadsheet_id:
            raise ValidationAppError(
                "Spreadsheet ID is required when Google Sheets is enabled"
            )

        settings = self.settings_service.get_settings()
        settings.google_sheets_enabled = enabled
        settings.google_sheets_spreadsheet_id = spreadsheet_id

        try:
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise ValidationAppError("Unable to save Google Sheets settings") from exc

        return self.get_settings_payload()

    def sync_completed_sessions(self) -> dict[str, object]:
        settings = self.get_settings_payload()
        self._validate_sync_configuration(settings)

        spreadsheet_id = str(settings["spreadsheet_id"])
        timezone_name = self.settings_service.get_settings().timezone
        sessions = sorted(
            self.repository.list_sessions(mode="work"),
            key=lambda session: session.completed_at_utc,
        )
        sheets_service = self._build_sheets_service()

        try:
            values_resource = sheets_service.spreadsheets().values()
            response = (
                values_resource.get(
                    spreadsheetId=spreadsheet_id,
                    range=self.SHEET_RANGE,
                ).execute()
                or {}
            )
            existing_values = response.get("values", [])
            existing_ids = self._prepare_sheet(
                values_resource,
                spreadsheet_id,
                existing_values,
            )
            rows = [
                self._build_session_row(session, timezone_name)
                for session in sessions
                if session.client_session_id not in existing_ids
            ]

            if rows:
                (
                    values_resource.append(
                        spreadsheetId=spreadsheet_id,
                        range=self.SHEET_RANGE,
                        valueInputOption="RAW",
                        insertDataOption="INSERT_ROWS",
                        body={"values": rows},
                    ).execute()
                )
        except ValidationAppError:
            raise
        except Exception as exc:  # pragma: no cover - external API wrapper
            current_app.logger.error(
                "Google Sheets sync failed (%s)",
                type(exc).__name__,
            )
            raise ValidationAppError(
                "Google Sheets sync failed. Check the spreadsheet ID, API access, "
                "credentials, and sharing permissions."
            ) from exc

        skipped = len(sessions) - len(rows)
        return {
            "status": "success",
            "spreadsheet_id": spreadsheet_id,
            "exported": len(rows),
            "skipped": skipped,
            "total_completed_work_sessions": len(sessions),
            "message": (
                f"Exported {len(rows)} completed work session(s); "
                f"skipped {skipped} duplicate(s)."
            ),
        }

    def _prepare_sheet(
        self,
        values_resource,
        spreadsheet_id: str,
        existing_values: list[list[object]],
    ) -> set[str]:
        if not existing_values:
            (
                values_resource.update(
                    spreadsheetId=spreadsheet_id,
                    range=self.HEADER_RANGE,
                    valueInputOption="RAW",
                    body={"values": [self.HEADERS]},
                ).execute()
            )
            return set()

        header = [str(value) for value in existing_values[0]]
        if header != self.HEADERS:
            raise ValidationAppError(
                "Google Sheets header row does not match the expected format"
            )

        return {
            str(row[0]).strip()
            for row in existing_values[1:]
            if row and str(row[0]).strip()
        }

    def _build_session_row(self, session, timezone_name: str) -> list[object]:
        started_local = to_local_datetime(session.started_at_utc, timezone_name)
        completed_local = to_local_datetime(session.completed_at_utc, timezone_name)
        created_local = to_local_datetime(session.created_at_utc, timezone_name)

        return [
            session.client_session_id,
            started_local.date().isoformat(),
            started_local.strftime("%H:%M:%S"),
            completed_local.strftime("%H:%M:%S"),
            session.planned_duration_seconds,
            session.actual_duration_seconds,
            session.mode,
            timezone_name,
            created_local.isoformat(),
        ]

    def _validate_sync_configuration(self, settings: dict[str, object]) -> None:
        if not settings["enabled"]:
            raise ValidationAppError("Google Sheets integration is disabled")
        if not settings["spreadsheet_id"]:
            raise ValidationAppError("Google Sheets spreadsheet ID is missing")
        if not settings["credentials_configured"]:
            raise ValidationAppError("Google Sheets credentials are missing")

        self._validate_spreadsheet_id(str(settings["spreadsheet_id"]))

    def _validate_spreadsheet_id(self, spreadsheet_id: str) -> None:
        if spreadsheet_id and not self.SPREADSHEET_ID_PATTERN.fullmatch(spreadsheet_id):
            raise ValidationAppError("Google Sheets spreadsheet ID is invalid")

    @classmethod
    def _build_sheets_service(cls):
        credentials_json = current_app.config["GOOGLE_SHEETS_CREDENTIALS_JSON"]

        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise ValidationAppError(
                "Google Sheets dependencies are missing. "
                "Run pip install -r requirements.txt."
            ) from exc

        try:
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError as exc:
            raise ValidationAppError(
                "GOOGLE_SHEETS_CREDENTIALS_JSON is not valid JSON"
            ) from exc

        try:
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=[cls.SHEETS_SCOPE],
            )
            return build(
                "sheets",
                "v4",
                credentials=credentials,
                cache_discovery=False,
            )
        except Exception as exc:  # pragma: no cover - dependency wrapper
            current_app.logger.error(
                "Google Sheets client initialization failed (%s)",
                type(exc).__name__,
            )
            raise ValidationAppError(
                "Google Sheets credentials are invalid or incomplete"
            ) from exc
