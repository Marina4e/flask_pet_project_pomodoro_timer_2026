from __future__ import annotations


def test_get_settings(client):
    response = client.get("/api/settings")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["theme"] == "system"
    assert payload["timezone"] == "UTC"
    assert payload["cycles_before_long_break"] == 4
    assert payload["auto_start_next_session"] is True
    assert payload["test_mode_enabled"] is True


def test_update_settings(client):
    response = client.put(
        "/api/settings",
        json={
            "work_duration_minutes": 30,
            "short_break_minutes": 10,
            "long_break_minutes": 15,
            "cycles_before_long_break": 5,
            "sound_enabled": False,
            "auto_start_next_session": False,
            "theme": "dark",
            "timezone": "Europe/Kyiv",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["work_duration_minutes"] == 30
    assert payload["sound_enabled"] is False
    assert payload["cycles_before_long_break"] == 5
    assert payload["auto_start_next_session"] is False
    assert payload["theme"] == "dark"


def test_update_settings_trims_timezone(client):
    response = client.put(
        "/api/settings",
        json={
            "work_duration_minutes": 25,
            "short_break_minutes": 5,
            "long_break_minutes": 15,
            "cycles_before_long_break": 4,
            "sound_enabled": True,
            "auto_start_next_session": True,
            "theme": "system",
            "timezone": " Europe/Kyiv ",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["timezone"] == "Europe/Kyiv"


def test_invalid_settings_returns_400(client):
    response = client.put(
        "/api/settings",
        json={
            "work_duration_minutes": 0,
            "short_break_minutes": 7,
            "long_break_minutes": 20,
            "cycles_before_long_break": 1,
            "sound_enabled": False,
            "auto_start_next_session": True,
            "theme": "neon",
            "timezone": "Invalid/Timezone",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "validation_error"
