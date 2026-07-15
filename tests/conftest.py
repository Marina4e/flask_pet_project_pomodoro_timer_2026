from __future__ import annotations

from datetime import UTC, datetime, timedelta
from itertools import count
from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from app.services.settings_service import SettingsService


@pytest.fixture()
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    monkeypatch.setenv("DEFAULT_TIMEZONE", "UTC")
    monkeypatch.setenv("GOOGLE_SHEETS_ENABLED", "false")
    monkeypatch.setenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
    monkeypatch.setenv("GOOGLE_SHEETS_CREDENTIALS_JSON", "")
    app = create_app("testing")
    app.config["DEFAULT_TIMEZONE"] = "UTC"

    with app.app_context():
        db.create_all()
        SettingsService().get_settings()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def session_payload_factory():
    counter = count(1)

    def factory(
        *,
        mode: str = "work",
        start_at: datetime | None = None,
        duration_seconds: int = 1500,
    ) -> dict[str, object]:
        index = next(counter)
        started_at = start_at or (
            datetime.now(UTC) - timedelta(seconds=duration_seconds + index)
        )
        completed_at = started_at + timedelta(seconds=duration_seconds)
        return {
            "client_session_id": f"session-{index:04d}",
            "mode": mode,
            "planned_duration_seconds": duration_seconds,
            "actual_duration_seconds": duration_seconds,
            "started_at_utc": started_at.isoformat().replace("+00:00", "Z"),
            "completed_at_utc": completed_at.isoformat().replace("+00:00", "Z"),
        }

    return factory


@pytest.fixture()
def persist_session(client, session_payload_factory):
    def _persist(**kwargs):
        payload = session_payload_factory(**kwargs)
        response = client.post("/api/sessions", json=payload)
        assert response.status_code == 201
        return response.get_json()

    return _persist
