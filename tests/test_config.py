from __future__ import annotations

from app.config import _get_test_mode_flag


def test_pomodoro_test_mode_reads_supported_variable(monkeypatch):
    monkeypatch.setenv("POMODORO_TEST_MODE", "true")

    assert _get_test_mode_flag(False) is True


def test_legacy_test_duration_variable_is_ignored(monkeypatch):
    monkeypatch.delenv("POMODORO_TEST_MODE", raising=False)
    monkeypatch.setenv("ENABLE_TEST_DURATIONS", "true")

    assert _get_test_mode_flag(False) is False
