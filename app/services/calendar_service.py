from __future__ import annotations

import calendar as calendar_module
from datetime import date

from app.repositories import SessionRepository
from app.time_utils import (
    local_date_to_utc_range,
    local_range_to_utc_range,
    to_local_datetime,
)


class CalendarService:
    def __init__(self, repository: SessionRepository | None = None) -> None:
        self.repository = repository or SessionRepository()

    def get_month_summary(
        self, *, year: int, month: int, timezone_name: str
    ) -> dict[str, object]:
        start_day = date(year, month, 1)
        _, days_in_month = calendar_module.monthrange(year, month)
        if month == 12:
            end_day = date(year + 1, 1, 1)
        else:
            end_day = date(year, month + 1, 1)

        start_utc, end_utc = local_range_to_utc_range(start_day, end_day, timezone_name)
        sessions = self.repository.get_completed_between(start_utc, end_utc)

        days: list[dict[str, object]] = []
        for day_number in range(1, days_in_month + 1):
            current_day = date(year, month, day_number)
            day_sessions = [
                session
                for session in sessions
                if to_local_datetime(session.completed_at_utc, timezone_name).date()
                == current_day
            ]
            focus_seconds = sum(
                item.actual_duration_seconds
                for item in day_sessions
                if item.mode == "work"
            )
            days.append(
                {
                    "date": current_day.isoformat(),
                    "session_count": len(day_sessions),
                    "completed_work_sessions": sum(
                        1 for item in day_sessions if item.mode == "work"
                    ),
                    "focus_minutes": round(focus_seconds / 60, 2),
                    "has_activity": bool(day_sessions),
                }
            )

        return {"year": year, "month": month, "days": days}

    def get_day_details(
        self, *, selected_day: date, timezone_name: str
    ) -> dict[str, object]:
        start_utc, end_utc = local_date_to_utc_range(selected_day, timezone_name)
        sessions = self.repository.get_completed_between(start_utc, end_utc)
        serialized_sessions = [
            {
                "id": session.id,
                "client_session_id": session.client_session_id,
                "mode": session.mode,
                "actual_duration_seconds": session.actual_duration_seconds,
                "started_at_local": to_local_datetime(
                    session.started_at_utc, timezone_name
                ).isoformat(),
                "completed_at_local": to_local_datetime(
                    session.completed_at_utc, timezone_name
                ).isoformat(),
            }
            for session in sessions
        ]

        focus_seconds = sum(
            item.actual_duration_seconds for item in sessions if item.mode == "work"
        )

        return {
            "date": selected_day.isoformat(),
            "timezone": timezone_name,
            "total_sessions": len(sessions),
            "completed_work_sessions": sum(
                1 for item in sessions if item.mode == "work"
            ),
            "focus_minutes": round(focus_seconds / 60, 2),
            "sessions": serialized_sessions,
        }
