from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TIMER_JS = (PROJECT_ROOT / "app/static/js/timer.js").read_text(encoding="utf-8")
TIMER_TEMPLATE = (PROJECT_ROOT / "app/templates/components/timer.html").read_text(
    encoding="utf-8"
)


def test_skip_button_is_between_reset_and_export_controls():
    reset_position = TIMER_TEMPLATE.index('id="reset-timer-button"')
    skip_position = TIMER_TEMPLATE.index('id="skip-timer-button"')
    export_position = TIMER_TEMPLATE.index('id="export-control"')

    assert reset_position < skip_position < export_position


def test_skip_starts_next_mode_without_saving_skipped_session():
    skip_function = TIMER_JS.split("function skipTimer()", 1)[1].split(
        "function prepareNextSession", 1
    )[0]

    assert "stopInterval()" in skip_function
    assert "getSkippedTransition" in skip_function
    assert "startTimer()" in skip_function
    assert "saveCompletedSession" not in skip_function


def test_skipped_focus_does_not_increment_completed_cycle_count():
    transition_function = TIMER_JS.split("function getSkippedTransition", 1)[1].split(
        "function formatDuration", 1
    )[0]

    assert 'currentMode === "work"' in transition_function
    assert 'nextMode: "short_break"' in transition_function
    assert "nextCycleCount: currentCycleCount" in transition_function
    assert "currentCycleCount + 1" not in transition_function


def test_skip_supports_breaks_and_is_bound_to_button():
    transition_function = TIMER_JS.split("function getSkippedTransition", 1)[1].split(
        "function formatDuration", 1
    )[0]

    assert "return getNextTransition(currentMode, currentCycleCount)" in (
        transition_function
    )
    assert 'elements.skip.addEventListener("click", skipTimer)' in TIMER_JS


def test_long_break_settings_include_25_minutes():
    assert '<option value="25">25</option>' in (
        PROJECT_ROOT / "app/templates/components/settings_panel.html"
    ).read_text(encoding="utf-8")
