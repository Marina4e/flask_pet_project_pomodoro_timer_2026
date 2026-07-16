# Current Status

## Implemented

- Flask application factory with automatic local SQLite bootstrap
- shared Flask extensions for SQLAlchemy, Flask-Migrate, and Flask-Smorest
- SQLAlchemy models for `work_sessions` and `user_settings`
- repository and service layers for sessions, settings, statistics, calendar, CSV, Google Calendar, and Google Sheets sync
- API routes for health, sessions, statistics, calendar, settings, export, Google Calendar, and Google Sheets
- Bootstrap 5.3 landing page with official-style carousel, state-driven clock, settings, statistics, calendar, and integration cards
- browser timer restoration through `localStorage`
- immediate `Skip` transition for work, short break, and long break without saving the skipped interval
- explicit `POMODORO_TEST_MODE` flow with `10s / 5s` preset
- read-only `scripts/check_database.py`
- automated pytest suite with mocked Google Calendar and Google Sheets success, duplicate protection, and controlled-error coverage
- GitHub Actions CI for compileall, Ruff, Black, dependency consistency, and
  pytest on Python 3.12, with status badges in both README files
- separate Ukrainian `README.md` and English `README.en.md`, both linking the
  standalone bilingual Google Cloud setup guide with safe Calendar test-session
  commands and exact button-state documentation

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
- The homepage carousel reuses `app/static/images/tomato-idle-transparent.png` on every
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

## 2026-07-15 Google Sheets and Clock Animation

- Added optional Google Sheets export without changing the existing Google
  Calendar integration.
- Safe Sheets settings (`enabled` and `spreadsheet_id`) persist in SQLite;
  service-account JSON remains server-only in `.env`.
- `POST /api/integrations/google-sheets/sync` exports completed `work` sessions
  and prevents duplicates by reading stable `client_session_id` values already
  present in the sheet.
- Added the dedicated service, schema, blueprint, migration, compact frontend
  accordion, and controlled error messages.
- Replaced the second timer tomato with a generated 3D clock. Ready, paused,
  completed, and reset states use a static PNG; running and resumed states load
  the GIF, and removing its `src` stops animation outside `running`.
- Full automated suite passes: `61 passed`.
- Playwright verified all clock states, reset without a new database record,
  Sheets settings persistence, missing-credentials feedback, preserved Calendar
  UI, no browser credential field, and a clean console in the final smoke.

## 2026-07-15 Timer Skip Control

- Added `Skip` next to `Reset` for work, short-break, and long-break modes.
- Skip discards the active interval, does not call the sessions API, and starts
  the next mode immediately even when auto-start is disabled.
- Skipped work does not increment the completed-work cycle counter; skipped
  long break starts a fresh cycle.
- Existing normal completion still persists both focus and break sessions, and
  statistics continue returning separate focus/break values plus total tracked
  time.
- Playwright verified both skip directions with zero inserted rows, then normal
  work/break completion with both modes stored and counted.
- Full automated suite passes: `65 passed`.

## 2026-07-15 Integration Guidance and Project Defense Documentation

- Rebuilt only the Google integration area as full-width cards with internal
  two-column setup guidance; the rest of the frontend architecture remains
  unchanged.
- Optional content is marked in green, while values required only after an
  integration is selected are marked in orange. Both layouts remain responsive
  and have no mobile horizontal overflow.
- Calendar status accepts a direct ID or normalizes an official Google embed
  URL with `src`; unsupported URLs are rejected before client creation.
- Calendar client initialization now converts malformed or incomplete
  service-account credentials into a controlled project error.
- Sheets disabled mode accepts blank settings without parsing credentials or
  creating a client. Enabled Save validates ID and required credential fields;
  Sync remains disabled until the saved configuration is ready.
- Sheets success responses now include `success` and `integration`, while safe
  readiness flags never expose credential contents.
- Added focused service/API/frontend tests for disabled startup, no client
  creation, credential validation, incomplete-session rejection, header reuse,
  Calendar independence, secret non-disclosure, and all integration buttons.
- Added `docs/PROJECT_DEFENSE_GUIDE.md` in Ukrainian with the application
  factory, environment table, models, routes, services, repositories, frontend
  flow, Google setup, tests, Docker, Mermaid diagrams, a 5–7 minute speech,
  live-demo checklist, and teacher Q&A.
- Verification: focused suite `32 passed`; full suite `79 passed`; compileall,
  Ruff, Black, all 7 JavaScript syntax checks, route listing, dependency check,
  and read-only SQLite inspection passed.
- Playwright used a separate temporary SQLite database. It verified the general
  Save Settings button, both Sheets buttons, Calendar Sync UI, controlled
  missing credentials, unsupported-URL rejection, desktop/dark/mobile layout, and a
  clean final console (`0` errors, `0` warnings).

## 2026-07-15 Initial Calendar Runtime Debugging and Bilingual Google Guide

- Reproduced the current local Calendar state without printing secrets:
  credentials are present, completed unsynced work session `#53` exists, but
  `GOOGLE_CALENDAR_ID` has URL form and therefore fails ID validation.
- Confirmed through the real Flask endpoint that Calendar status returns `200`
  with `configured=false` and the sync request returns the controlled `400`
  invalid-ID message before creating a Google client or mutating SQLite.
- Confirmed the frontend handler is `syncGoogleCalendar()`, calls the correct
  Calendar endpoint, and enables the button only for configured + existing +
  unsynced latest work.
- Added focused regressions for missing ID, missing credentials, no completed
  work, a completed 10-second work session, exclusion of a newer break,
  invalid-JSON secret non-disclosure, and Calendar/Sheets independence.
- Duplicate Calendar conflicts now return `session_id` and
  `sync_status=already_synced` without returning the external Google event ID.
- Split the project documentation into Ukrainian `README.md` and English
  `README.en.md`, and kept `docs/GOOGLE_INTEGRATIONS_GUIDE.md` as the standalone
  bilingual Google Cloud setup guide with
  exact button conditions, artificial-session commands, manual API calls,
  troubleshooting, notification boundaries, symbol responsibilities, Mermaid
  flow, official sources, and future improvements.
- Updated `.env.example` with Calendar-ID and one-line-JSON guidance while
  retaining only variables that the application actually reads. Calendar is
  optional through blank required values; the current implementation has no
  separate `GOOGLE_CALENDAR_ENABLED` flag.
- Focused Calendar/Sheets suite passes: `31 passed`; full suite passes:
  `85 passed`. Compileall, Ruff, Black, route listing, and `pip check` pass.
- A live temporary-database HTTP smoke created one 10-second completed `work`
  session through `POST /api/sessions`, confirmed it as the latest unsynced
  Calendar candidate, deleted it through the API, and did not use the user's
  SQLite database.
- At this stage a real event was not created because the old validator rejected
  the URL-shaped value. The later normalization section below records the
  successful real sync without changing the user's `.env`.

## 2026-07-15 Separate Ukrainian and English READMEs

- `README.md` now contains the Ukrainian project guide only.
- `README.en.md` contains the equivalent English project guide only.
- Both language files link directly to each other and to the standalone
  `docs/GOOGLE_INTEGRATIONS_GUIDE.md` setup guide for Pomodoro Timer, Google
  Cloud, Google Calendar, and Google Sheets.
- This correction changes documentation only; frontend, backend, integration
  behavior, configuration, and the user's SQLite database remain untouched.
- Markdown structure, language separation, local links, and `git diff --check`
  passed; the full automated suite remains green with `85 passed`.

## 2026-07-15 Calendar Embed Normalization, Real Sync, and GitHub CI

- Confirmed from the screenshot and live status that completed focus `#63` was
  unsynced and credentials were present, but the configured value was an
  official Google Calendar embed URL.
- `GoogleCalendarService` now accepts either a direct Calendar ID or an official
  Google Calendar URL with a non-empty `src`, decodes that value, and sends only
  the normalized ID to Google. Arbitrary URLs, HTML, and embed URLs without
  `src` remain invalid.
- Live status changed from `configured=false` to `configured=true` and reported
  that the Calendar ID was normalized; frontend readiness became true for
  `#63`.
- One real `POST /api/integrations/google-calendar/sync` succeeded with `200`,
  created the event for work `#63`, returned a Calendar link, and stored the
  duplicate-protection marker in SQLite.
- After that success the button is correctly disabled for `#63`; completing the
  next focus session makes a new unsynced work record and enables it again.
- Added `.github/workflows/ci.yml` for push, pull request, and manual runs on
  Python 3.12. Both README files now show CI, Python, and Flask badges.
- Focused Calendar/frontend verification passes: `16 passed`; Ruff, Black, and
  JavaScript syntax checks pass. Full project verification passes: `86 passed`;
  compileall and `pip check` also pass.
- Edge headless rendered the real homepage with `#63 (synced)`, the
  already-in-Calendar explanation, and the sync button disabled against a
  duplicate.

## 2026-07-16 Long Break Duration Fix

- Confirmed the reported behavior against the running app: `GET /api/settings`
  returned `work=25`, `short=5`, and the persisted `long=5`.
- The frontend mapping was correct; it used the saved `long_break_minutes` value.
- Changed the new default long-break duration to 25 minutes, allowed 25 in the
  API schema and service validation, and added 25 to the settings selector.
- Updated the current local `user_settings` row to `long_break_minutes=25`
  through the existing settings API without deleting or recreating SQLite.
- Browser verification now returns `25:00` for `long_break`, `05:00` for
  `short_break`, and `25:00` for `work`.

## 2026-07-16 Featured TimerProject Video

- Compressed `D:\Desktop\TimerProject.mp4` into
  `docs/videos/timer-project.mp4` without modifying the Desktop source file.
- The repository copy is H.264/AAC, 960x720, 63 seconds, and 8.2 MB, below the
  requested 10 MB limit.
- Added the featured video player and direct download link before the other
  video reports in both `README.md` and `README.en.md`.
- Masked the personal Google Calendar ID visible in the source recording before
  publishing the repository copy.

## 2026-07-16 English Video Reports

- Added three narrated MP4 reports under `docs/videos/`:
  `pomodoro-project-walkthrough.mp4`, `sqlite-database-report.mp4`, and
  `google-sheets-export-report.mp4`.
- The first video explains the browser-to-Flask-to-SQLite flow and the roles of
  `create_app`, `PomodoroTimerService`, the SQLAlchemy models, repositories,
  services, and Google integration services.
- The second video shows the real `instance/pomodoro.db` structure in DB Browser
  for SQLite and explains the three tables, indexes, models, and read-only
  inspection path.
- The third video shows the current Google Sheets export view from Chrome with
  row identifiers masked in the portfolio copy; no Sheet or SQLite data was
  changed while capturing the source screens.
- Both README files now place the three videos at the beginning with local MP4
  links and HTML video players.
- Temporary screenshots, narration WAV files, and render scripts are kept only
  in the local working area during production and are not part of the README
  deliverable.

## Known Limitations

- real Google Sheets writes were not tested with external credentials in this session
- Google API UI success paths were browser-tested with mocked responses; this is
  not evidence of access to a real external Calendar or Sheet
- active timer restoration is browser-local, not cross-device
- `/api/docs` still exists as a developer route from Flask-Smorest, but it is not part of the HR flow
- no authentication
- local SQLite is intended for education and demos, not serious production persistence

## Last Update Date

- 2026-07-16
