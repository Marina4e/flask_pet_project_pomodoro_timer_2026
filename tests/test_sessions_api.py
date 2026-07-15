from __future__ import annotations

from datetime import UTC, datetime, timedelta


def test_create_session(client, session_payload_factory):
    response = client.post("/api/sessions", json=session_payload_factory())

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["mode"] == "work"


def test_duplicate_session_returns_conflict(client, session_payload_factory):
    payload = session_payload_factory()

    first = client.post("/api/sessions", json=payload)
    second = client.post("/api/sessions", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.get_json()["error"]["code"] == "conflict"


def test_list_and_filter_sessions(client, persist_session):
    persist_session(mode="work")
    persist_session(mode="short_break", duration_seconds=300)

    response = client.get("/api/sessions?mode=short_break&timezone=UTC")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] == 1
    assert payload["sessions"][0]["mode"] == "short_break"


def test_filter_sessions_by_date(client, persist_session):
    old_start = datetime.now(UTC) - timedelta(days=2, minutes=30)
    today_start = datetime.now(UTC) - timedelta(minutes=30)
    persist_session(start_at=old_start)
    persist_session(start_at=today_start)

    today = datetime.now(UTC).date().isoformat()
    response = client.get(
        f"/api/sessions?date_from={today}&date_to={today}&timezone=UTC"
    )

    assert response.status_code == 200
    assert response.get_json()["total"] == 1


def test_get_session_detail_and_delete(client, session_payload_factory):
    create_response = client.post("/api/sessions", json=session_payload_factory())
    session_id = create_response.get_json()["id"]

    detail_response = client.get(f"/api/sessions/{session_id}")
    delete_response = client.delete(f"/api/sessions/{session_id}")

    assert detail_response.status_code == 200
    assert detail_response.get_json()["id"] == session_id
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Session deleted"


def test_invalid_session_payload_returns_400(client):
    response = client.post("/api/sessions", json={"mode": "work"})

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "validation_error"


def test_missing_session_returns_json_404(client):
    response = client.get("/api/sessions/999")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"
