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

- `GET /api/integrations/google-calendar/status` - safe configuration and
  latest-completed-work readiness state. `calendar_id_normalized=true` means
  the returned ID was decoded from an official Google Calendar embed URL `src`
- `POST /api/integrations/google-calendar/sync` - create one event for the
  latest completed unsynchronized `work` session; JSON body accepts optional
  `timezone`. The service sends a direct or normalized Calendar ID, never the
  full embed URL

## Google Sheets

- `GET /api/integrations/google-sheets/settings` - browser-safe enablement,
  Spreadsheet ID, and readiness flags; never returns credentials
- `PUT /api/integrations/google-sheets/settings` - save `enabled` and
  `spreadsheet_id`
- `POST /api/integrations/google-sheets/sync` - append missing completed
  `work` sessions and return exported/skipped counts

See `docs/GOOGLE_INTEGRATIONS_GUIDE.md` for PowerShell examples, error states,
test-session creation, and external Google setup.

## Developer-Only API Docs

- `GET /api/openapi.json`
- `GET /api/docs`
