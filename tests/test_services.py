from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from app.errors import ConflictAppError, ValidationAppError
from app.repositories import SessionRepository
from app.services.calendar_service import CalendarService
from app.services.csv_export_service import CSVExportService
from app.services.pomodoro_timer import PomodoroTimerService
from app.services.session_service import SessionService
from app.services.settings_service import SettingsService
from app.services.statistics_service import StatisticsService


def test_timer_start_pause_resume_reset_complete():
    service = PomodoroTimerService()
    started_at = datetime(2026, 7, 11, 10, 0, tzinfo=UTC)
    running = service.start(
        mode="work", duration_seconds=1500, started_at_utc=started_at
    )

    paused = service.pause(running, started_at + timedelta(minutes=10))
    assert paused.status == "paused"
    assert paused.remaining_seconds == 900

    resumed = service.resume(paused, started_at + timedelta(minutes=12))
    assert resumed.status == "running"
    assert resumed.expected_end_at_utc == started_at + timedelta(minutes=27)

    completed = service.complete(resumed, started_at + timedelta(minutes=27))
    assert completed.status == "completed"
    assert completed.remaining_seconds == 0

    reset = service.reset(mode="work", duration_seconds=1500)
    assert reset.status == "idle"
    assert reset.remaining_seconds == 1500


def test_timer_rejects_invalid_duration():
    service = PomodoroTimerService()

    with pytest.raises(ValidationAppError):
        service.start(
            mode="work",
            duration_seconds=0,
            started_at_utc=datetime.now(UTC),
        )


def test_session_service_prevents_duplicates(app, session_payload_factory):
    with app.app_context():
        service = SessionService()
        payload = session_payload_factory()
        service.create_session(payload)

        with pytest.raises(ConflictAppError):
            service.create_session(payload)


def test_statistics_calendar_and_csv_services(app, session_payload_factory):
    with app.app_context():
        session_service = SessionService()
        base_start = datetime(2026, 7, 11, 9, 0, tzinfo=UTC)
        session_service.create_session(
            session_payload_factory(start_at=base_start, duration_seconds=1500)
        )
        session_service.create_session(
            session_payload_factory(
                mode="short_break",
                start_at=base_start + timedelta(minutes=30),
                duration_seconds=300,
            )
        )

        statistics_service = StatisticsService()
        today = statistics_service.get_today_summary("UTC", date(2026, 7, 11))
        week = statistics_service.get_week_summary("UTC", date(2026, 7, 11))
        month = statistics_service.get_month_summary("UTC", date(2026, 7, 11))
        chart = statistics_service.get_chart_data("UTC", date(2026, 7, 11))

        assert today["completed_sessions"] == 2
        assert week["completed_work_sessions"] == 1
        assert month["break_minutes"] == 5.0
        assert len(chart["days"]) == 7

        calendar_service = CalendarService()
        month_summary = calendar_service.get_month_summary(
            year=2026,
            month=7,
            timezone_name="UTC",
        )
        day_details = calendar_service.get_day_details(
            selected_day=date(2026, 7, 11),
            timezone_name="UTC",
        )

        assert any(day["has_activity"] for day in month_summary["days"])
        assert day_details["total_sessions"] == 2

        repository = SessionRepository()
        csv_content = CSVExportService().build_csv(repository.list_sessions(), "UTC")
        assert "client_session_id" in csv_content
        assert "short_break" in csv_content


def test_settings_service_validates_payload(app):
    with app.app_context():
        service = SettingsService()

        with pytest.raises(ValidationAppError):
            service.update_settings(
                {
                    "work_duration_minutes": 0,
                    "short_break_minutes": 5,
                    "long_break_minutes": 15,
                    "cycles_before_long_break": 1,
                    "sound_enabled": True,
                    "auto_start_next_session": True,
                    "theme": "dark",
                    "timezone": "UTC",
                }
            )
