from __future__ import annotations

from datetime import UTC, datetime, timedelta


def test_export_csv(client, persist_session):
    persist_session()

    response = client.get("/api/export/sessions.csv?timezone=UTC")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert (
        "attachment; filename=pomodoro-sessions.csv"
        in response.headers["Content-Disposition"]
    )
    body = response.get_data(as_text=True)
    assert "client_session_id" in body
    assert "session-0001" in body


def test_export_csv_filters_single_day_range(client, persist_session):
    old_start = datetime.now(UTC) - timedelta(days=2, minutes=30)
    today_start = datetime.now(UTC) - timedelta(minutes=30)
    persist_session(start_at=old_start)
    persist_session(start_at=today_start)

    today = datetime.now(UTC).date().isoformat()
    response = client.get(f"/api/export/sessions.csv?date_from={today}&timezone=UTC")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "session-0002" in body
    assert "session-0001" not in body


def test_export_csv_rejects_invalid_range(client):
    response = client.get(
        "/api/export/sessions.csv?date_from=2026-07-11&date_to=2026-07-10&timezone=UTC"
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "validation_error"
