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

### Added — integration guidance and project defense

- Full-width Calendar and Sheets cards with green optional badges, orange
  conditional-required badges, button-specific explanations, setup steps, and
  explicit instructions for finding the external result.
- Safe readiness fields for Sheets and structured success metadata.
- Calendar ID prevalidation that rejects embed/share URLs before a Google
  client or network request is used.
- `tests/test_google_sheets_service.py` and
  `tests/test_integrations_frontend.py`, plus focused API regression scenarios.
- `docs/PROJECT_DEFENSE_GUIDE.md`, including code/data-flow explanations,
  environment/route/model tables, manual verification, a defense speech, demo
  checklist, and teacher questions.

### Changed — integration guidance and project defense

- Sheets enabled settings now validate the Spreadsheet ID and required
  service-account fields; disabled blank settings remain valid and lazy.
- Frontend handlers use explicit `syncGoogleCalendar()`,
  `saveGoogleSheetsSettings()`, and `syncGoogleSheets()` names.
- Sync buttons remain visible but disabled until their exact readiness
  conditions are satisfied.

### Verified — integration guidance and project defense

- focused integration/frontend suite — `32 passed`
- full pytest suite — `79 passed`
- compileall, Ruff, Black, and syntax checks for all 7 JavaScript files
- Flask route listing, `pip check`, Google client imports, and read-only SQLite
  inspection (`34` stored sessions)
- temporary-SQLite Playwright checks for all four visible Save/Sync buttons,
  embed-URL rejection, mocked success handlers, responsive layout, and final
  browser console with `0` errors and `0` warnings

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

## 2026-07-15 — Google Sheets and clock animation

### Added

- Dedicated Google Sheets service, schema, blueprint, settings endpoints, sync
  endpoint, environment variables, and Alembic migration.
- Compact `Google Sheets Settings` accordion with safe SQLite persistence for
  enablement and Spreadsheet ID.
- Mocked tests for disabled/missing/invalid configuration, successful export,
  duplicate prevention, work-only filtering, external error sanitization, and
  settings persistence.
- Generated 3D clock assets: a static PNG and an optimized 48-frame GIF with a
  slow 24-second loop.

### Changed

- Timer animation now loads the GIF only while running or resumed and returns
  to the static clock for ready, paused, completed, and reset states.
- Renamed the stale frontend `syncSheets()` Calendar handler to the explicit
  `syncGoogleCalendar()` and kept Google Calendar behavior unchanged.
- README now documents secure service-account setup, direct Sheet sharing,
  exported columns, duplicate rules, quotas, and current pricing caveat.

### Verified

- focused frontend and Sheets suite — `17 passed`
- full pytest suite — `61 passed`
- live temporary-SQLite browser smoke for clock and Sheets settings flows
- Google Calendar card remained present and the final browser console was clean
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

## 2026-07-15 — Timer Skip control

### Added

- `Skip` button beside `Reset` for work, short-break, and long-break modes.
- Focused frontend regression coverage for button placement, immediate mode
  transition, no save call, and completed-cycle preservation.

### Changed

- Skipping now discards the active interval and immediately starts the next
  countdown regardless of the auto-start setting.
- The testing fixture explicitly enables `POMODORO_TEST_MODE`, preventing local
  `.env` values from changing testing-config expectations.

### Verified

- focused timer/frontend suite — `12 passed`
- full pytest suite — `65 passed`
- Playwright verified work and break skipping with no inserted sessions
- normal work and short-break completion stored and counted both durations
- final browser console — `0 errors`, `0 warnings`

## 2026-07-15 — Calendar runtime debugging and bilingual Google documentation

### Added

- Bilingual `docs/GOOGLE_INTEGRATIONS_GUIDE.md` covering Calendar, Sheets,
  service-account setup, resource sharing, IDs, credentials conversion,
  artificial test sessions, API requests, notifications, troubleshooting,
  security, data flow, and exact symbol responsibilities.
- Focused Calendar tests for missing configuration parts, no completed work,
  10-second test-mode work, newer-break exclusion, malformed-credential
  non-disclosure, and Calendar/Sheets independence.

### Changed

- `README.md` is now one equivalent Ukrainian/English project guide with full
  startup, timer, SQLite, Google Cloud, Docker, verification, usability, and
  project-defense coverage.
- `.env.example` now distinguishes Calendar ID from URLs and explains the
  actual optional boundary without introducing an unused feature flag.
- Repeated Calendar sync errors no longer expose the external Google event ID;
  they return `session_id` plus `sync_status=already_synced`.
- API and file-map documentation now includes both Google integrations and the
  new guide.

### Verified

- real local status: invalid URL-shaped Calendar ID, structurally complete
  credential shape, unsynced completed work `#53`, button readiness false
- real local sync endpoint: controlled `400` before any external Google call
- focused Calendar/Sheets tests — `31 passed`
- full test suite — `85 passed`; compileall, Ruff, Black, route listing, and
  dependency consistency passed
- live artificial-session command — passed against a temporary SQLite database;
  created/detected/deleted one 10-second work record without touching user data
- no frontend template, CSS, timer, carousel, statistics UI, or calendar UI
  changes

## 2026-07-15 — Separate Ukrainian and English README files

### Added

- Added `README.en.md` as the English-only project guide.

### Changed

- `README.md` now contains only the Ukrainian project guide.
- Both README files link to each other and to the standalone bilingual
  `docs/GOOGLE_INTEGRATIONS_GUIDE.md` setup guide.
- Renamed the separate guide to make its Pomodoro Timer, Google Cloud, Google
  Calendar, and Google Sheets scope explicit, and added links back to both
  language README files.

### Scope

- Documentation-only correction; no frontend, backend, database, or integration
  behavior was changed.

### Verified

- Both README files contain all 19 numbered sections, balanced code fences, and
  valid local links; the English README contains no Cyrillic content.
- `git diff --check` passed apart from informational Windows line-ending
  warnings.
- Full pytest suite — `85 passed`.

## 2026-07-15 — Calendar embed normalization and GitHub CI

### Added

- Added `.github/workflows/ci.yml` with Python 3.12 dependency installation,
  compileall, Ruff, Black, `pip check`, and pytest for push, pull request, and
  manual workflow runs.
- Added CI, Python, and Flask badges to the Ukrainian and English README files.
- Added `calendar_id_normalized` to the safe Calendar status response.

### Changed

- Calendar configuration now accepts a direct Calendar ID or an official Google
  Calendar embed URL containing `src`; only the decoded ID reaches Google API.
- Unsupported URLs, HTML snippets, and embed URLs without `src` remain invalid.
- Calendar UI now explains when an ID was read from an embed URL and enables
  sync when all normal readiness conditions are satisfied.

### Verified

- Live status for work `#63`: configured, normalized, and ready to sync.
- Real Calendar sync: `200`, event created, Calendar link returned, and the
  SQLite duplicate marker stored for `#63`.
- Focused Calendar/frontend suite — `16 passed`; Ruff, Black, and JavaScript
  syntax checks passed.
- Full suite — `86 passed`; compileall and `pip check` passed.
- Edge headless rendered `#63 (synced)`, the already-synced message, and the
  expected duplicate-protection disabled button.

## 2026-07-16 — English video reports

### Added

- Added three English-voiced MP4 reports in `docs/videos/` covering the
  application architecture, the real SQLite database, and Google Sheets export.
- Added video players and direct MP4 links at the beginning of `README.md` and
  `README.en.md`.

### Changed

- The Google Sheets capture used in the portfolio videos masks row identifiers
  and excludes the browser address bar; the source Sheet and local SQLite data
  were not modified.

### Verified

- MP4 outputs are H.264 video at `1280x720` with AAC English narration.
- `pomodoro-project-walkthrough.mp4` — approximately 2:15.
- `sqlite-database-report.mp4` — approximately 1:34.
- `google-sheets-export-report.mp4` — approximately 1:33.

## 2026-07-16 — Long Break duration fix

### Fixed

- Changed the standard `long_break` duration from the previous default to 25
  minutes so the timer now matches the requested `25 / 5 / 25` setup.
- Allowed 25-minute long breaks in the Marshmallow API schema and
  `SettingsService` validation.
- Added the 25-minute option to the visible settings selector.
- Updated the existing local settings row through `PUT /api/settings`; the
  SQLite database was not deleted or recreated.

### Verified

- API settings response: `work=25`, `short=5`, `long=25`.
- Browser mode checks: Work `25:00`, Short break `05:00`, Long break `25:00`.

## 2026-07-16 — Featured TimerProject video

### Added

- Added `docs/videos/timer-project.mp4` as the first featured video in both
  README files.
- Compressed the 63-second source recording from 25.7 MB to 8.2 MB using
  960x720 H.264/AAC encoding.

### Changed

- Masked the personal Calendar ID visible in the source recording. The Desktop
  source file was not modified.

### Verified

- `ffprobe` confirms H.264 video, AAC audio, 960x720 resolution, and a file size
  below 10 MB.
