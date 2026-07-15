# Pomodoro Work Tracker

[![CI](https://github.com/Marina4e/flask_pet_project_pomodoro_timer_2026/actions/workflows/ci.yml/badge.svg)](https://github.com/Marina4e/flask_pet_project_pomodoro_timer_2026/actions/workflows/ci.yml)
![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Flask 3.1](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)

[Ukrainian README](README.md) ·
[Google Cloud setup: Pomodoro, Calendar, and Sheets](docs/GOOGLE_INTEGRATIONS_GUIDE.md) ·
[Project defense guide](docs/PROJECT_DEFENSE_GUIDE.md) ·
[API docs after startup](http://127.0.0.1:5000/api/docs)

Pomodoro Work Tracker is a single-user educational Flask application for focus
timing, completed-session tracking, statistics, an activity calendar, CSV
export, and optional Google Calendar and Google Sheets integrations.

> Google services are optional. The timer, SQLite, statistics, activity
> calendar, and CSV export work without Google credentials.

## English Version

### 1. Project purpose

`Pomodoro Work Tracker` alternates focus and break intervals, stores normally
completed sessions in a local SQLite database, and turns those records into
statistics, an activity calendar, and CSV exports. Optionally, a user can
manually:

- create a Google Calendar event for the latest completed `work` session;
- export completed `work` sessions as Google Sheets rows.

This is an educational portfolio project. It demonstrates the full path from a
browser timer to a Flask API, SQLAlchemy, migrations, external Google APIs,
tests, and Docker. It is not presented as an enterprise or multi-user SaaS.

### 2. Implemented features

- `Start`, `Pause`, `Resume`, `Reset`, and `Skip` for `work`, `short_break`, and
  `long_break`;
- automatic focus/break transitions and optional auto-start;
- active countdown recovery after reload through `localStorage`;
- storage of normally completed focus and break sessions in SQLite;
- separate `focus_minutes`, `break_minutes`, and `total_tracked_minutes`;
- daily, weekly, monthly statistics and a 7-day Chart.js chart;
- activity calendar with details for a selected day;
- duration, cycle, theme, sound, and IANA timezone settings;
- CSV export;
- fast `POMODORO_TEST_MODE` with `10 / 5 / 5` second intervals;
- manual optional Google Calendar and Google Sheets synchronization;
- OpenAPI/Swagger, pytest, Ruff, Black, Docker, and Gunicorn.

### 3. Technology stack

| Layer | Technologies |
| --- | --- |
| Backend | Python 3.12+, Flask, Flask-Smorest, Marshmallow |
| Data | Flask-SQLAlchemy, SQLite, Flask-Migrate/Alembic |
| Frontend | Jinja2, Bootstrap 5.3, Vanilla JavaScript, Chart.js |
| Google | Google Calendar API, Google Sheets API, service account |
| Quality | pytest, Ruff, Black, compileall |
| Deployment | Docker, Gunicorn, `start.sh` |

### 4. Quick Windows setup

```powershell
git clone <PROJECT_URL>
cd flask_pet_project_pomodoro_timer_2026

py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`. Press `Ctrl+C` to stop the server.

`create_app()` loads `.env`, registers extensions and blueprints, applies local
SQLite migrations, and creates default settings. A value already set in
PowerShell takes precedence over the same `.env` key. Restart the server after
editing `.env`.

### 5. Main environment variables

```dotenv
APP_ENV=development
SECRET_KEY=replace-with-a-secure-secret
DEBUG=true
DATABASE_URL=sqlite:///pomodoro.db
DEFAULT_TIMEZONE=Europe/Kyiv
DEFAULT_CYCLES_BEFORE_LONG_BREAK=4
POMODORO_TEST_MODE=false

# Google Calendar: optional; leave required values blank to keep it unconfigured.
GOOGLE_CALENDAR_ID=
GOOGLE_CALENDAR_CREDENTIALS_JSON=
GOOGLE_CALENDAR_EVENT_PREFIX=Pomodoro
GOOGLE_CALENDAR_EVENT_COLOR_ID=

# Google Sheets: independent and optional.
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_SHEETS_CREDENTIALS_JSON=
```

The current Calendar implementation has no separate
`GOOGLE_CALENDAR_ENABLED` flag. It remains unconfigured while either
`GOOGLE_CALENDAR_ID` or `GOOGLE_CALENDAR_CREDENTIALS_JSON` is blank. Sheets has
the separate `GOOGLE_SHEETS_ENABLED` flag and stores browser-safe settings in
SQLite.

Never commit or paste the real `.env`, service-account JSON, or private key into
Git, documentation, screenshots, or chat.

### 6. Test mode, Reset, and Skip

```powershell
$env:POMODORO_TEST_MODE="true"
python run.py
```

In test mode, `work` lasts 10 seconds and both break modes last 5 seconds. To
remove the temporary variable:

```powershell
Remove-Item Env:POMODORO_TEST_MODE
python run.py
```

Persistence rules:

- normal countdown completion creates a SQLite record;
- `Pause` does not complete or store a session;
- `Reset` discards the current interval and creates no record;
- `Skip` discards the current interval, creates no record, and starts the next mode;
- a completed 10-second test-mode `work` session is a normal record and is
  eligible for Calendar sync;
- Calendar does not sync break sessions, although normally completed breaks are
  stored and included in statistics.

### 7. SQLite, statistics, activity calendar, and CSV

The default local database is `instance/pomodoro.db`. Its main tables are:

- `work_sessions` — mode, planned/actual duration, UTC timestamps,
  `client_session_id`, and optional `google_calendar_event_id`;
- `user_settings` — timer settings, timezone, theme, sound, auto-start, and
  browser-safe Sheets settings;
- `alembic_version` — current migration revision.

Run the read-only inspector:

```powershell
python scripts/check_database.py
```

Pages and export:

- `/` — timer, settings, and optional integration cards;
- `/statistics` — today/week/month totals and the 7-day chart;
- `/calendar` — month activity view and day details;
- `/api/export/sessions.csv?timezone=Europe/Kyiv` — CSV download;
- `/api/docs` — Swagger UI.

Timestamps are stored in UTC. Statistics, calendar, CSV, and Google payloads
convert them to the selected IANA timezone, such as `Europe/Kyiv`.

### 8. Google Calendar: what the block means and why the button failed

`Save the latest focus session as an event` means: select the **latest completed
SQLite session with `mode="work"`** and manually create one Calendar event. It
does not mean a running/paused session, reset/skip, a break, or a work session
that was already synchronized.

The screenshot showed the exact cause of the disabled button: credentials and
completed work `#63` were ready, but `GOOGLE_CALENDAR_ID` contained an embed
URL. The backend previously returned `calendar_id_valid=false`, so `canSync()`
kept the button disabled.

The backend now safely recognizes an official Google Calendar embed URL,
decodes its `src` value as the Calendar ID, and sends only that normalized ID to
the API. A real verification created the Google event for work `#63` and stored
its event marker in SQLite. After success the button is intentionally disabled
again because `#63` is already synchronized. Complete the next focus session
and the button will automatically become available for that new record.

The button is always visible, but it is enabled only when all three conditions
are true:

```text
status.configured
AND status.latest_work_session_id exists
AND status.latest_work_session_synced is false
```

| Actual condition | Button state | Backend result |
| --- | --- | --- |
| ID or credentials are blank | Disabled, `Setup required` | `400`, not configured |
| Official embed URL contains `src` | Enabled when unsynced work exists | ID is decoded automatically |
| Other URL, share link, or HTML | Disabled, `Fix Calendar ID` | `400`, invalid Calendar ID |
| No completed `work` session | Disabled | `400`, no completed work session |
| Latest overall session is a break but an earlier work exists | Depends on work | Backend selects latest `work` only |
| Completed unsynced work exists | Enabled | Attempts `events.insert()` |
| Latest work already has an event ID | Disabled, `already synced` | `409 Conflict` for direct API call |
| JSON is incomplete/malformed | May be enabled because status checks presence | Safe `400` during sync |
| API/permission/network failure | Enabled before click | Safe `400`; secret details are not returned |

`configured=true` means the required values are present and the Calendar ID has
an acceptable shape. Full JSON validity, Google access, and sharing are checked
only during manual sync. Startup does not contact Google.

### 9. Google Calendar setup — short path

1. Create or select a Google Cloud project.
2. Enable the **Google Calendar API** under `APIs & Services`.
3. Create a service account under `IAM & Admin → Service Accounts`.
4. Download a JSON key from `Keys → Add key → Create new key`.
5. Copy `client_email` from that JSON.
6. Prefer a dedicated Pomodoro calendar in Google Calendar.
7. Open `Settings and sharing → Share with specific people or groups`, add the
   `client_email`, and grant **Make changes to events**.
8. Under `Integrate calendar`, preferably copy the **Calendar ID**. A complete
   official embed URL containing `src` also works; a Public URL, share link, or
   `<iframe>` does not.
9. Convert the JSON file to one line:

```powershell
(Get-Content .\service-account.json -Raw |
    ConvertFrom-Json |
    ConvertTo-Json -Compress)
```

Alternative:

```powershell
python -c "import json; print(json.dumps(json.load(open('service-account.json', encoding='utf-8')), separators=(',', ':')))"
```

10. Store both values only in the local `.env`:

```dotenv
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_CALENDAR_CREDENTIALS_JSON='{"type":"service_account","...":"..."}'
```

11. Restart Flask, complete a work session, and click
    `Sync to Google Calendar`.

A Google Cloud IAM role alone does **not** share a personal Calendar. Explicitly
share the specific calendar with `client_email`. Work/school domain policies may
restrict external sharing.

See the full bilingual guide, troubleshooting, and API flow:
[docs/GOOGLE_INTEGRATIONS_GUIDE.md](docs/GOOGLE_INTEGRATIONS_GUIDE.md).

### 10. Fast Calendar verification through test mode

1. Configure Calendar and restart Flask.
2. Set `POMODORO_TEST_MODE=true`.
3. Start `work` and let all 10 seconds finish.
4. Confirm that the Calendar card shows `ready to sync`.
5. Click `Sync to Google Calendar`.
6. Find the short event in the shared calendar at that session's time.
7. A second sync of the same work session is blocked.

Test mode creates real local records; it only shortens duration.

### 11. Artificial completed work session without waiting

No new development endpoint is necessary. The existing `POST /api/sessions`
safely creates one completed local record and does **not** call Google. Run Flask
and execute this in another PowerShell window:

```powershell
$completed = [DateTimeOffset]::UtcNow
$started = $completed.AddSeconds(-10)
$body = @{
  client_session_id = "calendar-test-$([guid]::NewGuid().ToString('N'))"
  mode = "work"
  planned_duration_seconds = 10
  actual_duration_seconds = 10
  started_at_utc = $started.ToString("o")
  completed_at_utc = $completed.ToString("o")
} | ConvertTo-Json

$created = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/sessions" `
  -ContentType "application/json" `
  -Body $body

$created
```

To use the browser button next, reload `/`: a POST from a separate PowerShell
window does not emit the browser's `pomodoro:sessions-changed` event. The direct
API sync below does not require a reload.

Then inspect status and sync:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/status"

$syncBody = @{ timezone = "Europe/Kyiv" } | ConvertTo-Json
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/sync" `
  -ContentType "application/json" `
  -Body $syncBody
```

Delete only the local test record when needed:

```powershell
Invoke-RestMethod `
  -Method Delete `
  -Uri "http://127.0.0.1:5000/api/sessions/$($created.id)"
```

If an external event was already created, deleting the local record does not
delete it from Google Calendar. Remove that event manually. Do not delete the
entire SQLite database for one test record.

### 12. Google Sheets — an independent optional integration

Calendar and Sheets do not call each other.

| Property | Google Calendar | Google Sheets |
| --- | --- | --- |
| Result | One Calendar event | New A:I rows |
| Source | Latest completed work | All completed work |
| Trigger | Manual button | Manual button |
| External resource | Shared Calendar | Shared Spreadsheet |
| Enable rule | ID + credentials | Enable + ID + credentials |
| Duplicate protection | Event ID in SQLite | `client_session_id` in column A |
| Break export | No | No |
| Independent | Works without Sheets | Works without Calendar |

Sheets setup:

1. Enable the **Google Sheets API** in the same or another Cloud project.
2. Create a Google Sheet manually.
3. Click `Share`, add the service-account `client_email` as **Editor**, and
   disable `Notify people` because a service account has no inbox.
4. Copy the ID between `/d/` and `/edit` in the URL.
5. Add the one-line JSON to `GOOGLE_SHEETS_CREDENTIALS_JSON` and restart Flask.
6. In `Google Sheets Settings`, enable the checkbox, enter the Spreadsheet ID,
   and click `Save Settings`.
7. Click `Sync Completed Sessions`.

`Save Settings` stores only the enable flag and Spreadsheet ID in SQLite and
validates server credentials, but it does not add rows. `Sync Completed
Sessions` creates a header in an empty sheet, appends only missing work
sessions, and skips duplicates.

### 13. Google notifications: precise behavior

The Flask application creates an event, but it does not implement push, email,
or browser notifications. A service account does not send a notification to
the user either. After event creation, Google Calendar applies the user's own
default or event-specific notification settings: email, desktop notification,
or Calendar alert.

Configure them in Google Calendar under
`Settings → Settings for my calendars → <calendar> → Event notifications`, or
open an individual event and add a reminder. The browser/OS must allow
notifications for `calendar.google.com`.

### 14. Manual verification API

| Method | URL | Body | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/integrations/google-calendar/status` | none | Safe Calendar status |
| `POST` | `/api/integrations/google-calendar/sync` | optional `timezone` | Sync latest work |
| `GET` | `/api/integrations/google-sheets/settings` | none | Browser-safe Sheets settings |
| `PUT` | `/api/integrations/google-sheets/settings` | `enabled`, `spreadsheet_id` | Save non-secret settings |
| `POST` | `/api/integrations/google-sheets/sync` | none | Export completed work |
| `POST` | `/api/sessions` | completed session payload | Create a local session |
| `DELETE` | `/api/sessions/<id>` | none | Delete one local record |

### 15. Architecture, files, and responsibilities

| File | Responsibility |
| --- | --- |
| `run.py` | Creates the app and starts the Flask development server |
| `app/__init__.py` | `create_app`, config, extensions, blueprints, SQLite bootstrap |
| `app/config.py` | Reads env and defines development/testing/production config |
| `app/models/work_session.py` | SQLAlchemy completed-session model |
| `app/repositories/session_repository.py` | Queries, including latest work |
| `app/services/session_service.py` | Validation and create/list/get/delete session use cases |
| `app/services/google_calendar_service.py` | Calendar status, payload, client, sync, duplicate guard |
| `app/services/google_sheets_service.py` | Settings, rows, header, and duplicate guard |
| `app/blueprints/integrations/routes.py` | Calendar status/sync endpoints |
| `app/blueprints/google_sheets/routes.py` | Sheets settings/sync endpoints |
| `app/static/js/integrations.js` | Browser status, button readiness, and API calls |
| `scripts/check_database.py` | Read-only SQLite inspection |
| `tests/test_integrations_api.py` | Mocked Calendar scenarios |
| `tests/test_google_sheets_api.py` | Mocked Sheets scenarios |
| `.env` | Local secrets; never committed |
| `.env.example` | Safe template without secrets |

Key symbols:

| Symbol | Input / result / side effect |
| --- | --- |
| `create_app(config_name=None)` | Builds Flask app; registers infrastructure; applies local SQLite migrations |
| `SessionService.create_session(payload)` | Validates a completed payload, stores `WorkSession`, returns a serialized dict |
| `SessionRepository.get_latest_work_session()` | Returns newest `mode="work"` by `completed_at_utc`; ignores breaks |
| `GoogleCalendarService.get_status()` | Returns safe readiness/latest-work state; no Google call |
| `sync_latest_work_session(timezone_name=None)` | Validates, creates event, stores Google event ID; may return `400/409` |
| `_build_event_payload(session, timezone_name)` | Builds summary, description, aware start/end, optional color |
| `_build_calendar_service()` | Lazily parses credentials and builds Calendar API client |
| `GoogleSheetsService.update_settings(payload)` | Stores only non-secret settings in SQLite |
| `sync_completed_sessions()` | Appends missing work rows and returns exported/skipped counts |
| Browser `canSync(status)` | Enables Calendar button only for all three readiness conditions |
| Browser `syncGoogleCalendar()` | POSTs timezone and renders success/error; never calls Sheets |

The detailed parameters, return values, errors, and callers are documented in
the [Google integrations guide](docs/GOOGLE_INTEGRATIONS_GUIDE.md).

### 16. Docker

```powershell
docker build -t pomodoro-work-tracker .
docker run --rm `
  -p 5000:5000 `
  --env-file .env `
  -v "${PWD}/instance:/app/instance" `
  pomodoro-work-tracker
```

The volume persists SQLite between containers. The production command in
`start.sh` applies migrations and starts Gunicorn. Do not bake `.env` into the
image.

### 17. Verification commands

```powershell
python -m compileall app scripts run.py
ruff check .
black --check .
pytest tests/test_integrations_api.py -v
pytest -v
flask --app run.py routes
python scripts/check_database.py
```

Automated Google tests use mocks and create no external events or rows. A real
external integration can be confirmed only with correctly configured
user-owned resources, API access, a service-account key, and sharing
permissions.

`.github/workflows/ci.yml` automatically runs compileall, Ruff, Black,
`pip check`, and the full pytest suite on Python 3.12 for every push, pull
request, and manual run. The `CI` badge at the top shows the latest GitHub
Actions status.

### 18. Usability, limitations, and project-defense value

The basic timer flow is straightforward: Google setup is not required, records
survive restarts, and test mode gives a fast demonstration. Google setup is a
more technical one-time step. The most common mistakes are confusing a resource
ID with its URL or forgetting to share the resource with `client_email`.

Known limitations:

- single-user application without authentication;
- countdown state lives in the browser; the server stores completion only;
- Calendar sync is manual, one-way, and limited to latest work;
- deleting a local record does not delete an existing Google event;
- Sheets export is manual and is not a real-time stream;
- Flask does not implement Google push notifications;
- SQLite and a JSON key in `.env` are suitable for local/portfolio demos, while
  production needs a managed database, secret manager, and considered OAuth/WIF
  flow.

The project's strength is the combination of Flask architecture with a real
optional Google Cloud integration model. It demonstrates application factory,
blueprints, schemas, SQLAlchemy, migrations, repositories/services,
UTC/timezone conversion, API errors, secure env configuration, service
accounts, Calendar/Spreadsheet sharing, external API mocks, and duplicate
protection. It provides practical experience with both Flask and Google Cloud /
Google Workspace APIs.

### 19. Documentation

- [Google Cloud setup guide for Calendar and Sheets](docs/GOOGLE_INTEGRATIONS_GUIDE.md)
  — Calendar, Sheets, test sessions, API, errors, secrets, and notifications;
- [Project Defense Guide](docs/PROJECT_DEFENSE_GUIDE.md) — architecture and
  defense scenario;
- [API Reference](docs/API_REFERENCE.md);
- [Deployment](docs/DEPLOYMENT.md);
- [Current Status](docs/CURRENT_STATUS.md).
