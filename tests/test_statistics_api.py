from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest


def test_today_week_month_statistics(client, persist_session):
    now = datetime.now(UTC)
    persist_session(start_at=now - timedelta(minutes=40), duration_seconds=1500)
    persist_session(
        mode="short_break",
        start_at=now - timedelta(minutes=15),
        duration_seconds=300,
    )

    today = client.get("/api/statistics/today?timezone=UTC")
    week = client.get("/api/statistics/week?timezone=UTC")
    month = client.get("/api/statistics/month?timezone=UTC")

    assert today.status_code == 200
    assert today.get_json()["completed_sessions"] == 2
    assert week.status_code == 200
    assert week.get_json()["completed_work_sessions"] == 1
    assert month.status_code == 200
    assert month.get_json()["focus_minutes"] == 25.0


def test_chart_endpoint_returns_seven_days(client, persist_session):
    now = datetime.now(UTC)
    persist_session(start_at=now - timedelta(days=1, minutes=20))
    persist_session(start_at=now - timedelta(days=3, minutes=20))

    response = client.get("/api/statistics/chart?timezone=UTC")

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["days"]) == 7


@pytest.mark.parametrize(
    ("endpoint", "timezone"),
    [
        ("/api/statistics/month", "Europe/Kyiv"),
        ("/api/statistics/week", "Europe/Kyiv"),
        ("/api/statistics/chart", "Europe/Kyiv"),
        ("/api/statistics/month", "UTC"),
        ("/api/statistics/week", "UTC"),
        ("/api/statistics/chart", "UTC"),
    ],
)
def test_statistics_endpoints_accept_supported_timezones(
    client, persist_session, endpoint, timezone
):
    now = datetime.now(UTC)
    persist_session(start_at=now - timedelta(minutes=35), duration_seconds=1500)

    response = client.get(f"{endpoint}?timezone={timezone}")

    assert response.status_code == 200


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/statistics/month",
        "/api/statistics/week",
        "/api/statistics/chart",
    ],
)
def test_statistics_endpoints_reject_invalid_timezone(client, endpoint):
    response = client.get(f"{endpoint}?timezone=Invalid/Timezone")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["details"]["timezone"] == "Invalid/Timezone"


def test_statistics_timezone_whitespace_is_normalized(client, persist_session):
    persist_session(duration_seconds=1500)

    response = client.get("/api/statistics/month?timezone=%20Europe/Kyiv%20")

    assert response.status_code == 200


def test_statistics_month_works_without_timezone_parameter(client, persist_session):
    now = datetime.now(UTC)
    persist_session(start_at=now - timedelta(minutes=35), duration_seconds=1500)

    response = client.get("/api/statistics/month")

    assert response.status_code == 200
    assert "focus_minutes" in response.get_json()
