from __future__ import annotations

from app.services.google_sheets_service import GoogleSheetsService


def test_application_starts_with_sheets_disabled_and_blank_configuration(app, client):
    assert app.config["GOOGLE_SHEETS_ENABLED"] is False
    assert app.config["GOOGLE_SHEETS_SPREADSHEET_ID"] == ""
    assert app.config["GOOGLE_SHEETS_CREDENTIALS_JSON"] == ""
    assert client.get("/api/health").status_code == 200


def test_disabled_status_does_not_parse_credentials_or_build_client(
    app,
    monkeypatch,
):
    app.config["GOOGLE_SHEETS_ENABLED"] = False
    app.config["GOOGLE_SHEETS_CREDENTIALS_JSON"] = "not-json-and-not-validated"
    monkeypatch.setattr(
        GoogleSheetsService,
        "_parse_credentials_info",
        classmethod(
            lambda cls: (_ for _ in ()).throw(
                AssertionError("Disabled integration must not parse credentials")
            )
        ),
    )
    monkeypatch.setattr(
        GoogleSheetsService,
        "_build_sheets_service",
        classmethod(
            lambda cls, credentials_info: (_ for _ in ()).throw(
                AssertionError("Disabled integration must not build a client")
            )
        ),
    )

    with app.app_context():
        service = GoogleSheetsService()
        payload = service.get_settings_payload()

    assert payload["enabled"] is False
    assert payload["credentials_configured"] is True


def test_disabled_sync_stops_before_client_creation(app, client, monkeypatch):
    monkeypatch.setattr(
        GoogleSheetsService,
        "_build_sheets_service",
        classmethod(
            lambda cls, credentials_info: (_ for _ in ()).throw(
                AssertionError("Disabled integration must not build a client")
            )
        ),
    )

    response = client.post("/api/integrations/google-sheets/sync", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "Google Sheets integration is disabled"
    )
