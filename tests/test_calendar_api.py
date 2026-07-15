from __future__ import annotations

from datetime import UTC, datetime, timedelta


def test_month_calendar_summary(client, persist_session):
    now = datetime.now(UTC)
    persist_session(start_at=now - timedelta(minutes=20))

    response = client.get(
        f"/api/calendar/month?year={now.year}&month={now.month}&timezone=UTC"
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["year"] == now.year
    assert any(day["has_activity"] for day in payload["days"])


def test_day_calendar_details(client, persist_session):
    now = datetime.now(UTC)
    persist_session(start_at=now - timedelta(minutes=20))
    response = client.get(
        f"/api/calendar/day?date={now.date().isoformat()}&timezone=UTC"
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total_sessions"] == 1
    assert len(payload["sessions"]) == 1
