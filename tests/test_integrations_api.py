from __future__ import annotations

from app.services.google_calendar_service import GoogleCalendarService


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
    assert "GOOGLE_CALENDAR_ID" in payload["missing"]


def test_google_calendar_sync_requires_configuration(client):
    response = client.post(
        "/api/integrations/google-calendar/sync",
        json={"timezone": "UTC"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "validation_error"


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
    assert second.get_json()["error"]["code"] == "conflict"


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
