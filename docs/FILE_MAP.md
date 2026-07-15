| File or directory | Purpose | When to change |
| --- | --- | --- |
| `app/__init__.py` | Flask application factory, env overrides, and local SQLite bootstrap | Change when startup flow or registration changes |
| `app/config.py` | Environment-based configuration rules | Change when env vars or config defaults change |
| `app/extensions.py` | Shared Flask extensions | Change when extensions are added or reconfigured |
| `app/models/` | SQLAlchemy models | Change when database structure changes |
| `app/repositories/` | Database query layer | Change when query behavior changes |
| `app/services/` | Business logic for timer, statistics, calendar, export, settings, Google Calendar, and Google Sheets | Change when behavior rules change |
| `app/services/google_calendar_service.py` | Google Calendar status + sync logic | Change when credentials flow, event payloads, or duplicate-sync rules change |
| `app/services/google_sheets_service.py` | Google Sheets settings, completed-work export, header validation, and duplicate prevention | Change when Sheets credentials, columns, or sync rules change |
| `app/blueprints/` | Page and API routes | Change when endpoints or page flows change |
| `app/blueprints/integrations/routes.py` | Google Calendar integration endpoints | Change when sync/status contracts change |
| `app/blueprints/google_sheets/routes.py` | Google Sheets settings and sync endpoints | Change when Sheets API contracts change |
| `app/api/schemas/` | Marshmallow API schemas | Change when payloads or responses change |
| `app/templates/` | Jinja page templates and components | Change when UI structure changes |
| `app/static/` | CSS and JavaScript assets | Change when frontend behavior or styling changes |
| `app/static/js/timer.js` | Browser timer logic | Change when timer states or UI flow change |
| `app/static/js/integrations.js` | Independent Google Calendar and Google Sheets frontend flows | Change when either integrations card changes |
| `app/static/images/clock-face-static.png` | Static 3D clock for non-running timer states | Change when the timer's resting visual changes |
| `app/static/images/clock-face.gif` | Optimized animated 3D clock for the running timer state | Change when the running visual changes |
| `scripts/check_database.py` | Read-only SQLite inspection helper | Change when table output or verification flow changes |
| `migrations/` | Alembic schema history | Change only when schema changes |
| `migrations/versions/5e7a9c2d4b11_add_google_sheets_settings.py` | Nullable safe Google Sheets settings in `user_settings` | Change only through a later migration |
| `tests/` | Automated verification suite | Change when behavior changes or regressions need coverage |
| `README.md` | User-facing setup and verification guide | Change when commands or visible behavior change |
| `IMPLEMENTATION_PLAN.md` | Current focused audit/fix plan | Change when the active implementation scope changes |
| `spec.md` | Internal file-routing guide for future work | Change when task routing guidance changes |
| `docs/` | Internal status, workflow, and verification notes | Change after important implementation or workflow changes |
