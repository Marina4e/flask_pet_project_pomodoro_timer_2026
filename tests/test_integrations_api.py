from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.google_calendar_service import GoogleCalendarService
from app.services.google_sheets_service import GoogleSheetsService


class _FakeInsertRequest:
    def execute(self):
        return {
            "id": "event-123",
            "htmlLink": "https://calendar.google.com/calendar/event?eid=test",
        }


class _FakeEventsResource:
    def __init__(self):
        self.last_calendar_id = None
        self.last_body = None

    def insert(self, *, calendarId, body):
        self.last_calendar_id = calendarId
        self.last_body = body
        return _FakeInsertRequest()


class _FakeCalendarService:
    def __init__(self):
        self.events_resource = _FakeEventsResource()

    def events(self):
        return self.events_resource


class _FailingInsertRequest:
    def execute(self):
        raise RuntimeError("private-external-details-must-not-leak")


class _FailingEventsResource:
    def insert(self, *, calendarId, body):
        return _FailingInsertRequest()


class _FailingCalendarService:
    def events(self):
        return _FailingEventsResource()


def test_google_calendar_status_reports_not_configured(client):
    response = client.get("/api/integrations/google-calendar/status")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["configured"] is False
    assert payload["calendar_id_valid"] is False
    assert "GOOGLE_CALENDAR_ID" in payload["missing"]


def test_google_calendar_normalizes_embed_url_before_sync(
    app, client, persist_session, monkeypatch
):
    fake_calendar_service = _FakeCalendarService()
    app.config["GOOGLE_CALENDAR_ID"] = (
        "https://calendar.google.com/calendar/embed?src=calendar%40example.com"
    )
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(lambda cls: fake_calendar_service),
    )
    persisted = persist_session()

    status_response = client.get("/api/integrations/google-calendar/status")
    sync_response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert status_response.status_code == 200
    status = status_response.get_json()
    assert status["configured"] is True
    assert status["calendar_id_valid"] is True
    assert status["calendar_id_normalized"] is True
    assert status["calendar_id"] == "calendar@example.com"
    assert sync_response.status_code == 200
    assert sync_response.get_json()["session_id"] == persisted["id"]
    assert fake_calendar_service.events_resource.last_calendar_id == (
        "calendar@example.com"
    )


def test_google_calendar_rejects_url_without_embed_source(app, client, monkeypatch):
    app.config["GOOGLE_CALENDAR_ID"] = (
        "https://calendar.google.com/calendar/embed?mode=week"
    )
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(
            lambda cls: (_ for _ in ()).throw(
                AssertionError("Calendar client must not be built for an invalid URL")
            )
        ),
    )

    status_response = client.get("/api/integrations/google-calendar/status")
    sync_response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert status_response.status_code == 200
    status = status_response.get_json()
    assert status["configured"] is False
    assert status["calendar_id_valid"] is False
    assert status["calendar_id_normalized"] is False
    assert sync_response.status_code == 400
    assert "embed URL containing src=" in str(sync_response.get_json())


def test_google_calendar_sync_requires_configuration(client):
    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "validation_error"


def test_google_calendar_sync_reports_missing_calendar_id(app, client):
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["details"]["missing"] == ["GOOGLE_CALENDAR_ID"]


def test_google_calendar_sync_reports_missing_credentials(app, client):
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["details"]["missing"] == [
        "GOOGLE_CALENDAR_CREDENTIALS_JSON"
    ]


def test_google_calendar_sync_requires_completed_work_session(
    app,
    client,
    monkeypatch,
):
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(
            lambda cls: (_ for _ in ()).throw(
                AssertionError("Calendar client must not be built without a session")
            )
        ),
    )

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "No completed work session is available to sync"
    )


def test_google_calendar_sync_succeeds_with_mocked_service(
    app, client, persist_session, monkeypatch
):
    fake_calendar_service = _FakeCalendarService()
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(lambda cls: fake_calendar_service),
    )
    persisted = persist_session()

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["session_id"] == persisted["id"]
    assert payload["event_id"] == "event-123"
    assert (
        fake_calendar_service.events_resource.last_calendar_id == "calendar@example.com"
    )
    assert (
        fake_calendar_service.events_resource.last_body["description"].find(
            persisted["client_session_id"]
        )
        >= 0
    )


def test_google_calendar_sync_accepts_ten_second_work_and_ignores_newer_break(
    app,
    client,
    persist_session,
    monkeypatch,
):
    fake_calendar_service = _FakeCalendarService()
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(lambda cls: fake_calendar_service),
    )
    work_start = datetime(2026, 7, 15, 18, 0, tzinfo=UTC)
    work_session = persist_session(
        mode="work",
        start_at=work_start,
        duration_seconds=10,
    )
    persist_session(
        mode="short_break",
        start_at=work_start + timedelta(seconds=20),
        duration_seconds=5,
    )

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "Europe/Kyiv"},
    )

    assert response.status_code == 200
    assert response.get_json()["session_id"] == work_session["id"]
    event = fake_calendar_service.events_resource.last_body
    assert event["summary"] == "Pomodoro focus session"
    assert "Duration (minutes): 0.17" in event["description"]
    assert event["start"]["timeZone"] == "Europe/Kyiv"
    assert event["end"]["timeZone"] == "Europe/Kyiv"


def test_google_calendar_invalid_credentials_do_not_leak(
    app,
    client,
    persist_session,
    caplog,
):
    secret = "not-json-private-calendar-key"
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = secret
    persist_session(duration_seconds=10)

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "GOOGLE_CALENDAR_CREDENTIALS_JSON is not valid JSON"
    )
    assert secret not in response.get_data(as_text=True)
    assert secret not in caplog.text


def test_google_calendar_sync_does_not_call_google_sheets(
    app,
    client,
    persist_session,
    monkeypatch,
):
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(lambda cls: _FakeCalendarService()),
    )
    monkeypatch.setattr(
        GoogleSheetsService,
        "sync_completed_sessions",
        lambda self: (_ for _ in ()).throw(
            AssertionError("Calendar sync must not call Sheets sync")
        ),
    )
    persist_session(duration_seconds=10)

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 200


def test_google_calendar_sync_prevents_repeat_sync(
    app, client, persist_session, monkeypatch
):
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(lambda cls: _FakeCalendarService()),
    )
    persist_session()

    first = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )
    second = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert first.status_code == 200
    assert second.status_code == 409
    error = second.get_json()["error"]
    assert error["code"] == "conflict"
    assert error["details"] == {
        "session_id": first.get_json()["session_id"],
        "sync_status": "already_synced",
    }
    assert "event-123" not in second.get_data(as_text=True)


def test_google_calendar_sync_returns_controlled_external_error(
    app, client, persist_session, monkeypatch, caplog
):
    app.config["GOOGLE_CALENDAR_ID"] = "calendar@example.com"
    app.config["GOOGLE_CALENDAR_CREDENTIALS_JSON"] = '{"type":"service_account"}'
    monkeypatch.setattr(
        GoogleCalendarService,
        "_build_calendar_service",
        classmethod(lambda cls: _FailingCalendarService()),
    )
    persist_session()

    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 400
    payload_text = str(response.get_json())
    assert "private-external-details-must-not-leak" not in payload_text
    assert "Check the Calendar ID" in payload_text
    assert "RuntimeError" in caplog.text
