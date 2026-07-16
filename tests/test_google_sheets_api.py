from __future__ import annotations

import json

from app.services.google_calendar_service import GoogleCalendarService
from app.services.google_sheets_service import GoogleSheetsService

SPREADSHEET_ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
VALID_CREDENTIALS = json.dumps(
    {
        "type": "service_account",
        "client_email": "pomodoro@example.iam.gserviceaccount.com",
        "private_key": "test-private-key",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
)


class _FakeRequest:
    def __init__(self, response=None, error: Exception | None = None):
        self.response = response or {}
        self.error = error

    def execute(self):
        if self.error is not None:
            raise self.error
        return self.response


class _FakeValuesResource:
    def __init__(self, existing_values=None, error: Exception | None = None):
        self.values = [list(row) for row in (existing_values or [])]
        self.error = error
        self.updated_headers = None
        self.appended_rows: list[list[object]] = []
        self.append_calls = 0

    def get(self, *, spreadsheetId, range):
        self.spreadsheet_id = spreadsheetId
        self.read_range = range
        return _FakeRequest(
            {"values": [list(row) for row in self.values]},
            error=self.error,
        )

    def update(self, *, spreadsheetId, range, valueInputOption, body):
        self.updated_headers = body["values"][0]
        self.values = [list(self.updated_headers)]
        return _FakeRequest({"updatedRows": 1})

    def append(
        self,
        *,
        spreadsheetId,
        range,
        valueInputOption,
        insertDataOption,
        body,
    ):
        rows = [list(row) for row in body["values"]]
        self.appended_rows.extend(rows)
        self.values.extend(rows)
        self.append_calls += 1
        return _FakeRequest({"updates": {"updatedRows": len(rows)}})


class _FakeSpreadsheetsResource:
    def __init__(self, values_resource):
        self.values_resource = values_resource

    def values(self):
        return self.values_resource


class _FakeSheetsService:
    def __init__(self, existing_values=None, error: Exception | None = None):
        self.values_resource = _FakeValuesResource(existing_values, error)

    def spreadsheets(self):
        return _FakeSpreadsheetsResource(self.values_resource)


def _configure_sheets(app, *, credentials=VALID_CREDENTIALS):
    app.config["GOOGLE_SHEETS_ENABLED"] = True
    app.config["GOOGLE_SHEETS_SPREADSHEET_ID"] = SPREADSHEET_ID
    app.config["GOOGLE_SHEETS_CREDENTIALS_JSON"] = credentials


def _mock_sheets_client(monkeypatch, fake_service):
    monkeypatch.setattr(
        GoogleSheetsService,
        "_build_sheets_service",
        classmethod(lambda cls, credentials_info: fake_service),
    )


def test_google_sheets_sync_rejects_disabled_integration(client):
    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "Google Sheets integration is disabled"
    )


def test_google_sheets_sync_requires_spreadsheet_id(app, client):
    app.config["GOOGLE_SHEETS_ENABLED"] = True
    app.config["GOOGLE_SHEETS_CREDENTIALS_JSON"] = '{"type":"service_account"}'

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "Google Sheets spreadsheet ID is missing"
    )


def test_google_sheets_sync_requires_credentials(app, client):
    _configure_sheets(app, credentials="")

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "Google Sheets credentials are missing"
    )


def test_google_sheets_sync_rejects_invalid_credentials_json(app, client):
    _configure_sheets(app, credentials="not-json")

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "GOOGLE_SHEETS_CREDENTIALS_JSON is not valid JSON"
    )


def test_google_sheets_sync_rejects_incomplete_credentials(app, client):
    _configure_sheets(app, credentials='{"type":"service_account"}')

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "Google Sheets credentials are invalid or incomplete"
    )
    assert set(response.get_json()["error"]["details"]["missing_fields"]) == {
        "client_email",
        "private_key",
        "token_uri",
    }


def test_google_sheets_sync_exports_completed_work_session(
    app,
    client,
    persist_session,
    monkeypatch,
):
    _configure_sheets(app)
    fake_service = _FakeSheetsService()
    _mock_sheets_client(monkeypatch, fake_service)
    session = persist_session(mode="work", duration_seconds=1500)

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["integration"] == "google_sheets"
    assert payload["exported"] == 1
    assert payload["skipped"] == 0
    assert fake_service.values_resource.updated_headers == GoogleSheetsService.HEADERS
    row = fake_service.values_resource.appended_rows[0]
    assert row[0] == session["client_session_id"]
    assert row[4:7] == [1500, 1500, "work"]
    assert row[7] == "UTC"


def test_google_sheets_sync_skips_session_ids_already_in_sheet(
    app,
    client,
    persist_session,
    monkeypatch,
):
    _configure_sheets(app)
    first = persist_session(mode="work")
    second = persist_session(mode="work")
    fake_service = _FakeSheetsService(
        [GoogleSheetsService.HEADERS, [first["client_session_id"]]]
    )
    _mock_sheets_client(monkeypatch, fake_service)

    first_response = client.post("/api/integrations/google-sheets/sync", json={})
    second_response = client.post("/api/integrations/google-sheets/sync", json={})

    assert first_response.status_code == 200
    assert first_response.get_json()["exported"] == 1
    assert first_response.get_json()["skipped"] == 1
    assert fake_service.values_resource.appended_rows[0][0] == (
        second["client_session_id"]
    )
    assert second_response.status_code == 200
    assert second_response.get_json()["exported"] == 0
    assert second_response.get_json()["skipped"] == 2
    assert fake_service.values_resource.append_calls == 1


def test_google_sheets_sync_exports_only_completed_work_mode_sessions(
    app,
    client,
    persist_session,
    monkeypatch,
):
    _configure_sheets(app)
    work_session = persist_session(mode="work")
    persist_session(mode="short_break")
    persist_session(mode="long_break")
    fake_service = _FakeSheetsService()
    _mock_sheets_client(monkeypatch, fake_service)

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 200
    assert response.get_json()["total_completed_work_sessions"] == 1
    assert [row[0] for row in fake_service.values_resource.appended_rows] == [
        work_session["client_session_id"]
    ]


def test_google_sheets_sync_reuses_existing_header(
    app,
    client,
    monkeypatch,
):
    _configure_sheets(app)
    fake_service = _FakeSheetsService([GoogleSheetsService.HEADERS])
    _mock_sheets_client(monkeypatch, fake_service)

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 200
    assert fake_service.values_resource.updated_headers is None
    assert fake_service.values_resource.append_calls == 0


def test_incomplete_session_request_is_not_exported(
    app,
    client,
    session_payload_factory,
    monkeypatch,
):
    payload = session_payload_factory(mode="work")
    payload.pop("completed_at_utc")
    rejected = client.post("/api/sessions", json=payload)
    _configure_sheets(app)
    fake_service = _FakeSheetsService()
    _mock_sheets_client(monkeypatch, fake_service)

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert rejected.status_code == 400
    assert response.status_code == 200
    assert response.get_json()["total_completed_work_sessions"] == 0
    assert fake_service.values_resource.append_calls == 0


def test_google_sheets_sync_does_not_call_google_calendar(
    app,
    client,
    persist_session,
    monkeypatch,
):
    _configure_sheets(app)
    fake_service = _FakeSheetsService()
    _mock_sheets_client(monkeypatch, fake_service)
    persist_session(mode="work")
    monkeypatch.setattr(
        GoogleCalendarService,
        "sync_latest_work_session",
        lambda self, timezone_name=None: (_ for _ in ()).throw(
            AssertionError("Sheets sync must not call Calendar sync")
        ),
    )

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 200
    assert response.get_json()["exported"] == 1


def test_google_sheets_sync_returns_controlled_external_error(
    app,
    client,
    monkeypatch,
    caplog,
):
    _configure_sheets(app)
    fake_service = _FakeSheetsService(
        error=RuntimeError("private-google-details-must-not-leak")
    )
    _mock_sheets_client(monkeypatch, fake_service)

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    payload_text = str(response.get_json())
    assert "private-google-details-must-not-leak" not in payload_text
    assert "Check the spreadsheet ID" in payload_text
    assert "RuntimeError" in caplog.text


def test_google_sheets_settings_save_safe_values_only(app, client):
    app.config["GOOGLE_SHEETS_CREDENTIALS_JSON"] = VALID_CREDENTIALS
    response = client.put(
        "/api/integrations/google-sheets/settings",
        json={"enabled": True, "spreadsheet_id": SPREADSHEET_ID},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {
        "enabled": True,
        "configured": True,
        "spreadsheet_id": SPREADSHEET_ID,
        "spreadsheet_id_valid": True,
        "credentials_configured": True,
        "credentials_valid": True,
    }

    saved = client.get("/api/integrations/google-sheets/settings")
    assert saved.status_code == 200
    assert saved.get_json() == payload
    response_text = saved.get_data(as_text=True)
    assert "credentials_json" not in response_text
    assert "private_key" not in response_text
    assert "client_email" not in response_text


def test_google_sheets_disabled_settings_accept_blank_values(client):
    response = client.put(
        "/api/integrations/google-sheets/settings",
        json={"enabled": False, "spreadsheet_id": ""},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "enabled": False,
        "configured": False,
        "spreadsheet_id": "",
        "spreadsheet_id_valid": False,
        "credentials_configured": False,
        "credentials_valid": False,
    }


def test_google_sheets_enabled_settings_require_server_credentials(client):
    response = client.put(
        "/api/integrations/google-sheets/settings",
        json={"enabled": True, "spreadsheet_id": SPREADSHEET_ID},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "Google Sheets credentials are missing"
    )


def test_google_sheets_sensitive_credentials_do_not_leak(
    app,
    client,
    caplog,
):
    secret = "PRIVATE-KEY-MUST-NOT-LEAK"
    _configure_sheets(
        app,
        credentials=json.dumps({"type": "service_account", "private_key": secret}),
    )

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    assert secret not in response.get_data(as_text=True)
    assert secret not in caplog.text
