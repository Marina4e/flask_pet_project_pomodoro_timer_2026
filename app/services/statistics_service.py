from __future__ import annotations

from datetime import date, timedelta

from app.repositories import SessionRepository
from app.time_utils import local_range_to_utc_range, to_local_datetime


class StatisticsService:
    def __init__(self, repository: SessionRepository | None = None) -> None:
        self.repository = repository or SessionRepository()

    def get_today_summary(
        self, timezone_name: str, current_day: date
    ) -> dict[str, object]:
        return self._build_summary(
            label="today",
            start_day=current_day,
            end_day_exclusive=current_day + timedelta(days=1),
            timezone_name=timezone_name,
        )

    def get_week_summary(
        self, timezone_name: str, current_day: date
    ) -> dict[str, object]:
        start_day = current_day - timedelta(days=current_day.weekday())
        return self._build_summary(
            label="week",
            start_day=start_day,
            end_day_exclusive=start_day + timedelta(days=7),
            timezone_name=timezone_name,
        )

    def get_month_summary(
        self, timezone_name: str, current_day: date
    ) -> dict[str, object]:
        start_day = current_day.replace(day=1)
        if start_day.month == 12:
            end_day = start_day.replace(year=start_day.year + 1, month=1)
        else:
            end_day = start_day.replace(month=start_day.month + 1)
        return self._build_summary(
            label="month",
            start_day=start_day,
            end_day_exclusive=end_day,
            timezone_name=timezone_name,
        )

    def get_chart_data(
        self, timezone_name: str, current_day: date, days: int = 7
    ) -> dict[str, object]:
        start_day = current_day - timedelta(days=days - 1)
        start_utc, end_utc = local_range_to_utc_range(
            start_day,
            current_day + timedelta(days=1),
            timezone_name,
        )
        sessions = self.repository.get_completed_between(start_utc, end_utc)

        points: list[dict[str, object]] = []
        for offset in range(days):
            day = start_day + timedelta(days=offset)
            focus_seconds = 0
            work_sessions = 0
            for session in sessions:
                local_day = to_local_datetime(
                    session.completed_at_utc, timezone_name
                ).date()
                if local_day != day:
                    continue
                if session.mode == "work":
                    work_sessions += 1
                    focus_seconds += session.actual_duration_seconds
            points.append(
                {
                    "date": day.isoformat(),
                    "focus_minutes": round(focus_seconds / 60, 2),
                    "completed_work_sessions": work_sessions,
                }
            )

        return {"days": points}

    def _build_summary(
        self,
        *,
        label: str,
        start_day: date,
        end_day_exclusive: date,
        timezone_name: str,
    ) -> dict[str, object]:
        start_utc, end_utc = local_range_to_utc_range(
            start_day,
            end_day_exclusive,
            timezone_name,
        )
        sessions = self.repository.get_completed_between(start_utc, end_utc)

        focus_seconds = sum(
            item.actual_duration_seconds for item in sessions if item.mode == "work"
        )
        break_seconds = sum(
            item.actual_duration_seconds for item in sessions if item.mode != "work"
        )
        work_sessions = sum(1 for item in sessions if item.mode == "work")

        return {
            "label": label,
            "start_date": start_day.isoformat(),
            "end_date": (end_day_exclusive - timedelta(days=1)).isoformat(),
            "completed_sessions": len(sessions),
            "completed_work_sessions": work_sessions,
            "focus_minutes": round(focus_seconds / 60, 2),
            "break_minutes": round(break_seconds / 60, 2),
            "total_tracked_minutes": round((focus_seconds + break_seconds) / 60, 2),
        }
