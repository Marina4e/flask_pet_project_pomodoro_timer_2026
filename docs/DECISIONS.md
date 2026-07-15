# Decisions

## Why the Flask application factory is used

- It keeps configuration selection explicit.
- It avoids a giant global app object.
- It makes testing easier because each test can create a fresh app instance.

## Why Blueprints are used

- They separate pages, settings, statistics, sessions, calendar, export, and health concerns.
- They keep routes shorter and easier to reason about.

## Why the timer runs mainly in the browser

- A second-by-second server-side timer would waste Flask worker time.
- Browser timing plus `localStorage` is enough for a single-user MVP.

## Why completed sessions are stored through Flask

- Statistics and calendar features need durable completed-session records.
- Backend persistence keeps browser reloads and app restarts from losing history.

## Why every second is not stored in the database

- It would add noise, write volume, and unnecessary complexity.
- Only the completed session matters for this MVP’s reporting rules.

## Why repositories and services are separated

- Repositories focus on database access.
- Services focus on business rules and aggregation.
- This keeps routes thin and services testable without HTML.

## Why UTC is stored

- UTC avoids ambiguous local timestamps.
- Timezone conversion happens only when presenting statistics or calendar views.

## Why SQLite is used locally

- It is simple for education and local development.
- It works well with Flask-Migrate and small demo datasets.

## How PostgreSQL can be enabled later

- Set `DATABASE_URL` to a PostgreSQL connection string.
- No route or service rewrite is required because SQLAlchemy abstracts the storage layer.

## How duplicate sessions are prevented

- Each completed session includes a `client_session_id`.
- The database has a unique constraint on that value.
- The service also checks before insert to return a domain-level conflict error.

## Why Gunicorn is used in production

- It is the expected Linux WSGI server for platforms such as Render.
- The startup flow in `start.sh` keeps production launch consistent.
