# Current Status

## Implemented

- Flask application factory with automatic local SQLite bootstrap
- shared Flask extensions for SQLAlchemy, Flask-Migrate, and Flask-Smorest
- SQLAlchemy models for `work_sessions` and `user_settings`
- repository and service layers for sessions, settings, statistics, calendar, CSV, and Google Calendar sync
- API routes for health, sessions, statistics, calendar, settings, export, and Google Calendar status/sync
- Bootstrap 5.3 landing page with official-style carousel, timer, settings, statistics, calendar, and sync card
- browser timer restoration through `localStorage`
- explicit `POMODORO_TEST_MODE` flow with `10s / 5s` preset
- read-only `scripts/check_database.py`
- automated pytest suite with mocked Google Calendar success and duplicate-sync coverage

## Verified In This Session

- `pytest tests/test_pages.py tests/test_statistics_api.py -v`
- `python -m compileall app`
- `ruff check .`
- `black --check .`
- `pytest -v`
- `pytest tests/test_pages.py -v`
- live HTTP smoke via local Flask server:
  - `/` returned `200`
  - `/api/statistics/month?timezone=Europe/Kyiv` returned `200`
  - `/api/statistics/week?timezone=Europe/Kyiv` returned `200`
  - `/api/statistics/chart?timezone=Europe/Kyiv` returned `200`
  - `/api/statistics/month?timezone=UTC` returned `200`
- browser smoke via Playwright + Edge headless:
  - home page carousel opened on `1366x768` and `390x844`
  - first slide was active
  - `Previous` and `Next` controls worked on desktop and mobile
  - slide indicators switched to the expected slides
  - `Open Calendar` opened `/calendar`
  - `Open Settings` changed the URL hash to `#settings-panel`
  - no horizontal overflow was detected
  - browser console had no errors

## 2026-07-15 Frontend Cleanup and Timezone Settings

- Visible frontend copy is now English across the home, statistics, calendar,
  settings, timer, integration, and error pages.
- The homepage carousel reuses `app/static/images/tomato-idle.png` on every
  slide, with compact image-and-text layout and mobile image-first ordering.
- Removed the redundant feature teaser row, compacted spacing, converted action
  controls to Bootstrap-compatible button markup, and moved secondary settings
  into a Bootstrap accordion.
- Settings now show the active IANA timezone, the `Europe/Kyiv` example, and the
  helper text `Used for daily, weekly, and monthly statistics.`
- Shared `get_timezone()` validation trims surrounding whitespace and keeps
  invalid values as controlled validation errors. Settings save the normalized
  value and restore the previous valid form state after a failed save.
- The original project-runtime `400` was caused by the Windows `.venv` missing
  the `tzdata` package; the system Python check alone did not reproduce it.
  `tzdata>=2024.1` is now declared in `requirements.txt` and verified in the
  project virtualenv.
- Focused and full tests pass: `45 passed`.
- Live HTTP smoke passes for `Europe/Kyiv` and `UTC` with `200`, and for
  `Invalid/Timezone` with `400` on month, week, and chart endpoints.
- The requested Windows browser smoke was attempted but stopped because the
  browser-control safety layer could not determine the current Chrome URL.

## Known Limitations

- real Google Calendar event creation was not tested with external credentials in this session
- active timer restoration is browser-local, not cross-device
- `/api/docs` still exists as a developer route from Flask-Smorest, but it is not part of the HR flow
- no authentication
- local SQLite is intended for education and demos, not serious production persistence

## Last Update Date

- 2026-07-15
