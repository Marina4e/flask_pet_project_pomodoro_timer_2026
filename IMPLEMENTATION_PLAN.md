# Pomodoro Work Tracker Implementation Plan

## Current state

The project already has the core Flask structure, timer UI, statistics, calendar,
CSV export, and automated tests. The main gaps against the current task are:
fresh local startup without manual database preparation, explicit test-mode
behavior, and the wrong external integration target.

## Required fixes

- [x] Make local SQLite startup work on first run without manual `flask db upgrade`
- [x] Switch test mode to explicit `POMODORO_TEST_MODE` behavior
- [x] Restrict settings to the allowed duration options from the task
- [x] Replace Google Sheets snapshot sync with simple Google Calendar sync
- [x] Add a read-only SQLite inspection script
- [ ] Finish documentation alignment with the audited project state

## Files to modify

- `app/__init__.py`
- `app/config.py`
- `app/models/work_session.py`
- `app/repositories/session_repository.py`
- `app/services/`
- `app/blueprints/integrations/routes.py`
- `app/api/schemas/`
- `app/templates/`
- `app/static/js/`
- `tests/`
- `scripts/check_database.py`
- `README.md`
- `docs/*`

## Out of scope

- FastAPI
- Swagger expansion
- Authentication
- PostgreSQL as the default local database
- Redis
- Celery
- Complex two-way Google Calendar synchronization
- New pages outside the current Flask UI
