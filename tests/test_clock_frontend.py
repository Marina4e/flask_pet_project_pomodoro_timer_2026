from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TIMER_JS = (PROJECT_ROOT / "app/static/js/timer.js").read_text(encoding="utf-8")
CLOCK_TEMPLATE = (
    PROJECT_ROOT / "app/templates/components/tomato_runner.html"
).read_text(encoding="utf-8")
CLOCK_CSS = (PROJECT_ROOT / "app/static/css/styles.css").read_text(encoding="utf-8")


def test_clock_ready_uses_static_asset_without_loading_animation():
    assert 'data-runner="idle"' in CLOCK_TEMPLATE
    assert "images/clock-face-static.png" in CLOCK_TEMPLATE
    assert 'data-animated-src="{{ url_for' in CLOCK_TEMPLATE
    assert 'animatedAsset.removeAttribute("src")' in TIMER_JS


def test_clock_running_and_resume_load_animated_asset():
    assert 'state.status = "running"' in TIMER_JS
    assert 'animatedAsset.setAttribute("src", animatedSrc)' in TIMER_JS
    assert '[data-runner="running"] .tomato-asset-running' in CLOCK_CSS


def test_clock_pause_and_completion_return_to_static_asset():
    assert 'state.status = "paused"' in TIMER_JS
    assert 'state.status = "completed"' in TIMER_JS
    assert '[data-runner="paused"] .tomato-asset-idle' in CLOCK_CSS
    assert '[data-runner="completed"] .tomato-asset-idle' in CLOCK_CSS


def test_clock_reset_returns_to_idle_without_saving_a_session():
    reset_function = TIMER_JS.split("function resetTimer()", 1)[1].split(
        "async function completeTimer", 1
    )[0]

    assert "state = defaultState" in reset_function
    assert "saveCompletedSession" not in reset_function
    assert '[data-runner="idle"] .tomato-asset-idle' in CLOCK_CSS
