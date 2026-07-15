# API Reference

## Pages

- `GET /` - dashboard page
- `GET /statistics` - statistics page
- `GET /calendar` - calendar page

## Health

- `GET /api/health`

## Sessions

- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/<session_id>`
- `DELETE /api/sessions/<session_id>`

## Statistics

- `GET /api/statistics/today?timezone=...`
- `GET /api/statistics/week?timezone=...`
- `GET /api/statistics/month?timezone=...`
- `GET /api/statistics/chart?timezone=...`

## Calendar

- `GET /api/calendar/month?year=YYYY&month=MM&timezone=...`
- `GET /api/calendar/day?date=YYYY-MM-DD&timezone=...`

## Settings

- `GET /api/settings`
- `PUT /api/settings`

## Export

- `GET /api/export/sessions.csv?timezone=...`

## Google Calendar

- `GET /api/integrations/google-calendar/status`
- `POST /api/integrations/google-calendar/sync`

## Developer-Only API Docs

- `GET /api/openapi.json`
- `GET /api/docs`
