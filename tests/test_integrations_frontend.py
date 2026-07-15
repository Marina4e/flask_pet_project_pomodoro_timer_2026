from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTEGRATIONS_JS = (PROJECT_ROOT / "app/static/js/integrations.js").read_text(
    encoding="utf-8"
)
INDEX_TEMPLATE = (PROJECT_ROOT / "app/templates/index.html").read_text(encoding="utf-8")


def test_integration_buttons_have_separate_explicit_handlers():
    assert "async function syncGoogleCalendar()" in INTEGRATIONS_JS
    assert "async function saveGoogleSheetsSettings()" in INTEGRATIONS_JS
    assert "async function syncGoogleSheets()" in INTEGRATIONS_JS
    assert (
        'window.pomodoroApi.put(\n          "/api/integrations/google-sheets/settings"'
        in (INTEGRATIONS_JS)
    )
    assert (
        'window.pomodoroApi.post(\n          "/api/integrations/google-sheets/sync"'
        in (INTEGRATIONS_JS)
    )


def test_sync_buttons_start_disabled_until_server_reports_readiness():
    calendar_button = INDEX_TEMPLATE.split('id="google-calendar-sync-button"', 1)[
        1
    ].split(">", 1)[0]
    sheets_button = INDEX_TEMPLATE.split('id="google-sheets-sync-button"', 1)[1].split(
        ">", 1
    )[0]

    assert "disabled" in calendar_button
    assert "disabled" in sheets_button
    assert "status?.configured" in INTEGRATIONS_JS
    assert "settings?.enabled && settings.configured" in INTEGRATIONS_JS


def test_optional_and_required_setup_are_visually_identified():
    assert "requirement-badge-optional" in INDEX_TEMPLATE
    assert "requirement-badge-required" in INDEX_TEMPLATE
    assert "The timer, focus and break statistics" in INDEX_TEMPLATE
    assert "Do not copy the embed URL" in INDEX_TEMPLATE
    assert 'id="google-sheets-credentials-input"' not in INDEX_TEMPLATE
