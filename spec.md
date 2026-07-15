# Pomodoro Work Tracker Working Spec

## Goal

Keep future work focused, economical, and file-specific.

## Mandatory First Reads For Any New Task

1. `docs/PROJECT_CONTEXT.md`
2. `docs/CURRENT_STATUS.md`
3. `docs/FILE_MAP.md`
4. `spec.md`

## File Routing Matrix

### If the task is about timer behavior

Read:
- `app/static/js/timer.js`
- `app/templates/components/timer.html`
- `app/services/pomodoro_timer.py`
- `app/services/settings_service.py`

### If the task is about statistics or calendar output

Read:
- `app/services/statistics_service.py`
- `app/services/calendar_service.py`
- `app/repositories/session_repository.py`
- the matching page JS

### If the task is about settings

Read:
- `app/models/user_settings.py`
- `app/services/settings_service.py`
- `app/api/schemas/settings.py`
- `app/blueprints/settings/routes.py`
- `app/static/js/settings.js`

### If the task is about Google Calendar

Read:
- `app/services/google_calendar_service.py`
- `app/blueprints/integrations/routes.py`
- `app/api/schemas/google_calendar.py`
- `app/static/js/integrations.js`
- `.env.example`
- README Google Calendar section

### If the task is about SQLite verification

Read:
- `app/__init__.py`
- `app/config.py`
- `scripts/check_database.py`
- `migrations/`
