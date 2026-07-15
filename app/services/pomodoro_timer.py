from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.errors import ValidationAppError
from app.time_utils import ensure_utc

ALLOWED_TIMER_MODES = {"work", "short_break", "long_break"}
ALLOWED_TIMER_STATUSES = {"idle", "running", "paused", "completed"}


@dataclass(slots=True)
class TimerState:
    mode: str
    status: str
    duration_seconds: int
    remaining_seconds: int
    started_at_utc: datetime | None = None
    expected_end_at_utc: datetime | None = None
    paused_at_utc: datetime | None = None
    completed_at_utc: datetime | None = None


class PomodoroTimerService:
    def start(
        self, *, mode: str, duration_seconds: int, started_at_utc: datetime
    ) -> TimerState:
        self._validate_mode(mode)
        self._validate_duration(duration_seconds)

        started_at = ensure_utc(started_at_utc)
        expected_end_at = started_at + self._seconds(duration_seconds)

        return TimerState(
            mode=mode,
            status="running",
            duration_seconds=duration_seconds,
            remaining_seconds=duration_seconds,
            started_at_utc=started_at,
            expected_end_at_utc=expected_end_at,
        )

    def pause(self, state: TimerState, paused_at_utc: datetime) -> TimerState:
        if state.status != "running" or state.expected_end_at_utc is None:
            raise ValidationAppError("Timer can only be paused while running")

        paused_at = ensure_utc(paused_at_utc)
        remaining = self.calculate_remaining_seconds(state, paused_at)

        return TimerState(
            mode=state.mode,
            status="paused",
            duration_seconds=state.duration_seconds,
            remaining_seconds=remaining,
            started_at_utc=state.started_at_utc,
            expected_end_at_utc=state.expected_end_at_utc,
            paused_at_utc=paused_at,
        )

    def resume(self, state: TimerState, resumed_at_utc: datetime) -> TimerState:
        if state.status != "paused" or state.paused_at_utc is None:
            raise ValidationAppError("Timer can only be resumed from paused state")

        resumed_at = ensure_utc(resumed_at_utc)
        expected_end_at = resumed_at + self._seconds(state.remaining_seconds)

        return TimerState(
            mode=state.mode,
            status="running",
            duration_seconds=state.duration_seconds,
            remaining_seconds=state.remaining_seconds,
            started_at_utc=state.started_at_utc,
            expected_end_at_utc=expected_end_at,
        )

    def reset(self, *, mode: str, duration_seconds: int) -> TimerState:
        self._validate_mode(mode)
        self._validate_duration(duration_seconds)
        return TimerState(
            mode=mode,
            status="idle",
            duration_seconds=duration_seconds,
            remaining_seconds=duration_seconds,
        )

    def complete(self, state: TimerState, completed_at_utc: datetime) -> TimerState:
        completed_at = ensure_utc(completed_at_utc)
        return TimerState(
            mode=state.mode,
            status="completed",
            duration_seconds=state.duration_seconds,
            remaining_seconds=0,
            started_at_utc=state.started_at_utc,
            expected_end_at_utc=state.expected_end_at_utc,
            completed_at_utc=completed_at,
        )

    def calculate_remaining_seconds(
        self, state: TimerState, current_at_utc: datetime
    ) -> int:
        if state.status == "paused":
            return max(state.remaining_seconds, 0)
        if state.expected_end_at_utc is None:
            raise ValidationAppError("Running timer state is missing expected end time")

        current_at = ensure_utc(current_at_utc)
        remaining = int((state.expected_end_at_utc - current_at).total_seconds())
        return max(remaining, 0)

    @staticmethod
    def _seconds(value: int):
        from datetime import timedelta

        return timedelta(seconds=value)

    @staticmethod
    def _validate_mode(mode: str) -> None:
        if mode not in ALLOWED_TIMER_MODES:
            raise ValidationAppError(
                "Unsupported timer mode",
                details={"mode": mode, "allowed": sorted(ALLOWED_TIMER_MODES)},
            )

    @staticmethod
    def _validate_duration(duration_seconds: int) -> None:
        if duration_seconds <= 0:
            raise ValidationAppError("Timer duration must be greater than zero")
