from __future__ import annotations

import csv
import io

from app.models import WorkSession
from app.time_utils import to_local_datetime


class CSVExportService:
    def build_csv(self, sessions: list[WorkSession], timezone_name: str) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "id",
                "client_session_id",
                "mode",
                "planned_duration_seconds",
                "actual_duration_seconds",
                "started_at_local",
                "completed_at_local",
            ]
        )

        for session in sessions:
            writer.writerow(
                [
                    session.id,
                    session.client_session_id,
                    session.mode,
                    session.planned_duration_seconds,
                    session.actual_duration_seconds,
                    to_local_datetime(
                        session.started_at_utc, timezone_name
                    ).isoformat(),
                    to_local_datetime(
                        session.completed_at_utc, timezone_name
                    ).isoformat(),
                ]
            )

        return buffer.getvalue()
