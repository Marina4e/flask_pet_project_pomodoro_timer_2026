from __future__ import annotations

from marshmallow import Schema, fields


class GoogleCalendarStatusSchema(Schema):
    configured = fields.Bool(required=True)
    calendar_id = fields.Str(required=True, allow_none=True)
    missing = fields.List(fields.Str(), required=True)
    latest_work_session_id = fields.Int(required=False, allow_none=True)
    latest_work_session_synced = fields.Bool(required=True)


class GoogleCalendarSyncRequestSchema(Schema):
    timezone = fields.Str(load_default=None)


class GoogleCalendarSyncSchema(Schema):
    status = fields.Nested(GoogleCalendarStatusSchema, required=True)
    timezone = fields.Str(required=True)
    session_id = fields.Int(required=True)
    event_id = fields.Str(required=True)
    html_link = fields.Str(required=False, allow_none=True)
