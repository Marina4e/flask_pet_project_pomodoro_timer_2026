## 2026-07-11

### Added
- Complete Flask application structure with application factory, extensions, Blueprints, models, repositories, and services
- Pomodoro dashboard, statistics page, calendar page, and responsive styling
- REST API with Flask-Smorest, Marshmallow validation, OpenAPI JSON, and Swagger UI
- SQLite-backed persistence, Alembic migration scaffold, and initial migration
- Pytest suite with API, page, factory, and service coverage
- Dockerfile, `start.sh`, `render.yaml`, `.env.example`, and project documentation set

### Changed
- Implemented browser-side timer restoration through `localStorage`
- Centralized API and page error handling
- Added timezone-aware statistics and calendar aggregation based on UTC storage
- Aligned calendar month navigation so day details stay within the visible month

### Fixed
- Normalized API output schemas to match ISO string response payloads
- Sanitized 422 validation error details so JSON errors remain serializable
- Corrected the test fixture to bind the SQLite test database before SQLAlchemy initialization
- Fixed CSV export filtering so `date_from` or `date_to` can be used independently
- Rejected reversed CSV export date ranges with a structured validation error

### Verified
- `python -m compileall app run.py wsgi.py`
- `flask --app run.py routes`
- `flask --app run.py db upgrade`
- `pytest -v tests/test_export_api.py`
- `black tests/test_export_api.py`
- `ruff check app/blueprints/export/routes.py tests/test_export_api.py`
- `ruff check .`
- `black --check .`
- `pytest -v`
- `pytest --cov=app --cov-report=term-missing`
- `python -c "from app import create_app; app = create_app('production'); print(app.config['ENV_NAME'])"`
- local HTTP health smoke check via `Invoke-RestMethod`
- `python -c "import pathlib; data = pathlib.Path('start.sh').read_bytes(); print('CRLF' if b'\\r\\n' in data else 'LF')"`

## 2026-07-14

### Added
- `IMPLEMENTATION_PLAN.md` with the focused audit and fix scope
- `scripts/check_database.py` for read-only SQLite inspection
- mocked successful Google Calendar sync test
- duplicate Google Calendar sync prevention test
- `google_calendar_event_id` persistence in `work_sessions`

### Changed
- local startup now auto-applies migrations for SQLite
- explicit `POMODORO_TEST_MODE` replaced the old implicit demo flag
- settings validation now accepts only the allowed duration choices
- Google Sheets snapshot sync was replaced with simple Google Calendar sync
- main UI copy now uses `Pomodoro Work Tracker`
- README and internal docs were rewritten to match the audited project state

### Fixed
- `.env` values are now applied at app-creation time instead of too late during imports
- first local run no longer fails on missing `user_settings` table
- `python run.py` can create a fresh SQLite database automatically

## 2026-07-15

### Changed

- Compact frontend spacing and reordered the homepage into carousel, timer,
  statistics, and settings sections.
- Translated visible frontend text to English and added responsive carousel
  image-and-text layouts using the existing tomato asset.
- Added a compact four-card statistics row and Bootstrap Advanced Settings
  accordion.
- Added visible timezone helper text and active-timezone output to the settings
  form.

### Fixed

- Central timezone validation now trims surrounding whitespace before resolving
  an IANA timezone, while invalid values still return controlled `400` errors.
- Failed timezone saves show a field-level message and restore the previous
  valid settings in the form.
- Added `tzdata>=2024.1` for stable Windows `zoneinfo` support after reproducing
  the original `Europe/Kyiv` failure in the project `.venv`.
- Added regression coverage for invalid timezone responses on month, week, and
  chart statistics endpoints.

### Verified

- `python -m compileall app scripts run.py`
- `ruff check .`
- `black --check .`
- `node --check` for every file in `app/static/js/`
- `pytest -v` — `45 passed`
- live HTTP smoke for valid `Europe/Kyiv` / `UTC` and invalid timezone values

### Verified
- `python -m compileall app scripts run.py`
- `ruff check .`
- `black --check .`
- `pytest -v`
- `flask --app run.py routes`
- fresh SQLite startup smoke with a clean temporary database
- `python scripts/check_database.py`
- browser smoke for timer controls and calendar navigation via Playwright

## 2026-07-14

### Added
- Bootstrap 5.3 landing page structure with carousel hero and brighter portfolio styling
- Animated running tomato visual tied to timer start/pause/resume state
- Configurable `cycles_before_long_break` and `auto_start_next_session` settings persisted in the database
- Optional Google Sheets integration with status endpoint, manual sync endpoint, and landing-page sync card
- New tests for Google Sheets integration status and sync configuration failure

### Changed
- Reworked the main dashboard to foreground `Часы за день`, `Часы за неделю`, and `Часы за месяц`
- Updated the timer UX to include demo preset `10с / 5с`, auto-cycling, and clearer status messaging
- Adjusted Ruff configuration to ignore local virtualenv noise so `ruff check .` validates repository code instead of site-packages
- Updated `.env.example`, README, and docs to reflect the new timer/settings/integration flow
- Removed extra hero CTA buttons, moved `Export CSV` into the timer card, and hid Google Sheets sync until configuration exists
- Swapped the previous tomato SVG for a more cartoon-style character with clearer idle vs running presentation

### Documented
- Added detailed README guidance for every `.env` variable
- Added step-by-step Google Sheets setup instructions including how to find spreadsheet ID and compress service-account JSON
- Added `spec.md` and `docs/STEP_BY_STEP_PLAN.md` for future economical file-by-file work

### Fixed
- Prevented the main lint command from scanning `.venv`
- Added the required migration for new timer-cycle settings so `flask --app run.py db upgrade` stays valid

### Verified
- `python -m compileall app run.py wsgi.py`
- `black app/services/google_sheets_service.py`
- `ruff check .`
- `black --check .`
- `flask --app run.py routes`
- `flask --app run.py db upgrade`
- `pytest -v`
- `pytest --cov=app --cov-report=term-missing`

## 2026-07-14

### Added
- regression tests for `timezone=Europe/Kyiv`, `timezone=UTC`, missing timezone, and invalid timezone on statistics endpoints
- home-page assertions for the Bootstrap carousel structure, indicators, prev/next controls, and section deeplinks

### Changed
- rebuilt the landing carousel around the Bootstrap 5.3 example structure with five slides for timer, statistics, calendar, settings, and Google Calendar sync
- kept carousel prev/next controls visible on mobile and aligned the slide layout for `390x844`
- added a small inline favicon so the landing page no longer triggers a browser `404` on load

### Fixed
- confirmed that `Europe/Kyiv` does not return `400` on the current backend and locked that behavior with tests instead of speculative service changes
- removed the remaining browser-console error during carousel smoke checks

### Verified
- `pytest tests/test_pages.py tests/test_statistics_api.py -v`
- `python -m compileall app`
- `ruff check .`
- `black --check .`
- `pytest -v`
- `pytest tests/test_pages.py -v`
- live HTTP smoke for `/`, `/api/statistics/month?timezone=Europe/Kyiv`, `/api/statistics/week?timezone=Europe/Kyiv`, `/api/statistics/chart?timezone=Europe/Kyiv`, and `/api/statistics/month?timezone=UTC`
- Playwright + Edge headless smoke for carousel controls, indicators, deeplinks, mobile layout, and console cleanliness
