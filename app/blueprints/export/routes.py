from __future__ import annotations

from datetime import timedelta

from flask import Response
from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.session import ExportQuerySchema
from app.errors import ValidationAppError
from app.services.csv_export_service import CSVExportService
from app.services.session_service import SessionService
from app.services.settings_service import SettingsService
from app.time_utils import local_range_to_utc_range

export_blp = Blueprint(
    "export",
    __name__,
    url_prefix="/api/export",
    description="CSV export endpoints",
)


@export_blp.route("/sessions.csv")
class SessionExportResource(MethodView):
    @export_blp.arguments(ExportQuerySchema, location="query")
    def get(self, query_args):
        timezone_name = (
            query_args.get("timezone") or SettingsService().get_settings().timezone
        )
        service = SessionService()
        start_day = query_args.get("date_from")
        end_day = query_args.get("date_to")

        if start_day is not None or end_day is not None:
            effective_start = start_day or end_day
            effective_end = end_day or start_day
            if effective_start is None or effective_end is None:
                raise ValidationAppError("Invalid export date range")
            if effective_end < effective_start:
                raise ValidationAppError(
                    "date_to must not be earlier than date_from",
                    details={
                        "date_from": effective_start.isoformat(),
                        "date_to": effective_end.isoformat(),
                    },
                )
            start_utc, end_utc = local_range_to_utc_range(
                effective_start,
                effective_end + timedelta(days=1),
                timezone_name,
            )
            sessions = service.repository.get_completed_between(start_utc, end_utc)
        else:
            sessions = service.repository.list_sessions()

        csv_content = CSVExportService().build_csv(sessions, timezone_name)
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=pomodoro-sessions.csv"
            },
        )
