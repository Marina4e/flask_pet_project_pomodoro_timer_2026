| File or directory | Purpose | When to change |
| --- | --- | --- |
| `app/__init__.py` | Flask application factory, env overrides, and local SQLite bootstrap | Change when startup flow or registration changes |
| `app/config.py` | Environment-based configuration rules | Change when env vars or config defaults change |
| `app/extensions.py` | Shared Flask extensions | Change when extensions are added or reconfigured |
| `app/models/` | SQLAlchemy models | Change when database structure changes |
| `app/repositories/` | Database query layer | Change when query behavior changes |
| `app/services/` | Business logic for timer, statistics, calendar, export, settings, and Google Calendar | Change when behavior rules change |
| `app/services/google_calendar_service.py` | Google Calendar status + sync logic | Change when credentials flow, event payloads, or duplicate-sync rules change |
| `app/blueprints/` | Page and API routes | Change when endpoints or page flows change |
| `app/blueprints/integrations/routes.py` | Google Calendar integration endpoints | Change when sync/status contracts change |
| `app/api/schemas/` | Marshmallow API schemas | Change when payloads or responses change |
| `app/templates/` | Jinja page templates and components | Change when UI structure changes |
| `app/static/` | CSS and JavaScript assets | Change when frontend behavior or styling changes |
| `app/static/js/timer.js` | Browser timer logic | Change when timer states or UI flow change |
| `app/static/js/integrations.js` | Google Calendar status and sync button logic | Change when the integrations card changes |
| `scripts/check_database.py` | Read-only SQLite inspection helper | Change when table output or verification flow changes |
| `migrations/` | Alembic schema history | Change only when schema changes |
| `tests/` | Automated verification suite | Change when behavior changes or regressions need coverage |
| `README.md` | User-facing setup and verification guide | Change when commands or visible behavior change |
| `IMPLEMENTATION_PLAN.md` | Current focused audit/fix plan | Change when the active implementation scope changes |
| `spec.md` | Internal file-routing guide for future work | Change when task routing guidance changes |
| `docs/` | Internal status, workflow, and verification notes | Change after important implementation or workflow changes |
