# Architecture

## Layers

- `app/__init__.py`: creates the Flask app, loads config, initializes extensions, registers Blueprints and error handlers
- `app/extensions.py`: shared `db`, `migrate`, and `api` objects
- `app/models/`: SQLAlchemy table definitions
- `app/repositories/`: focused database access methods
- `app/services/`: timer rules, settings logic, statistics aggregation, calendar aggregation, CSV generation
- `app/blueprints/`: page and API endpoints
- `app/api/schemas/`: Marshmallow validation and response contracts
- `app/templates/` and `app/static/`: Jinja-rendered frontend with JS enhancements

## Request Flow

1. Browser requests a page or API route.
2. Flask routes the request to a Blueprint endpoint.
3. Flask-Smorest and Marshmallow validate JSON or query arguments for API routes.
4. Route handlers delegate business logic to services.
5. Services call repositories for database access when needed.
6. Repositories use SQLAlchemy queries or persistence operations.
7. Results are serialized back to HTML, JSON, or CSV.

## Timer Architecture

- Active countdown state lives in the browser
- `timer.js` stores the active timer in `localStorage`
- The backend is notified only when a session is completed
- `client_session_id` prevents duplicate inserts

## Persistence

- `work_sessions`: completed timer sessions
- `user_settings`: single-user configuration row
- Timestamps are stored as UTC and converted on read

## Frontend Composition

- `index.html`: timer, settings, dashboard cards, chart, export link
- `statistics.html`: metrics and chart
- `calendar.html`: month grid and selected-day details
- JS files are split by concern: API, theme, settings, timer, statistics, calendar

## Deployment

- Linux production entrypoint is `./start.sh`
- `start.sh` runs migrations then starts Gunicorn
- `render.yaml` configures a Python web service
- Database backend is controlled through `DATABASE_URL`
