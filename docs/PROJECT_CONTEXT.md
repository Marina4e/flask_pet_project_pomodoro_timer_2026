# Project Context

Pomodoro Work Tracker is a single-user educational Flask project. It focuses on
simple local startup, readable Flask architecture, and browser-visible features
that a reviewer can inspect quickly.

## Main Features

- work, short-break, and long-break timer modes
- `Start`, `Pause`, `Resume`, `Reset`, `Skip`
- local test mode via `POMODORO_TEST_MODE=true`
- automatic local SQLite initialization on first run
- completed-session persistence in SQLite
- daily, weekly, and monthly statistics
- 7-day productivity chart
- activity calendar with day details
- settings persistence
- CSV export
- simple Google Calendar sync for the latest completed work session

## Business Rules

- active countdown state lives in the browser
- completed sessions are saved through Flask API
- skipped focus and break intervals are not saved; the next mode starts immediately
- completed focus and break durations are tracked separately and combined in total time
- duplicate session inserts are prevented by `client_session_id`
- Google Calendar duplicate sync is prevented by `google_calendar_event_id`
- stored timestamps are UTC; display conversions use the selected timezone

## Local Database Rules

- local default database URL stays `sqlite:///pomodoro.db`
- in Flask this resolves to `instance/pomodoro.db`
- local startup creates the SQLite file and applies migrations automatically
- local verification should not require a separate SQLite GUI

## Boundaries

- single-user only
- no authentication
- no background queue
- no paid hosting requirement
- no complex two-way Google Calendar synchronization
