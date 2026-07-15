from __future__ import annotations

from marshmallow import Schema, fields, validate


class SessionSchema(Schema):
    id = fields.Int(required=True)
    client_session_id = fields.Str(required=True)
    mode = fields.Str(required=True)
    planned_duration_seconds = fields.Int(required=True)
    actual_duration_seconds = fields.Int(required=True)
    started_at_utc = fields.Str(required=True)
    completed_at_utc = fields.Str(required=True)
    google_calendar_event_id = fields.Str(required=False, allow_none=True)
    created_at_utc = fields.Str(required=True)


class SessionCreateSchema(Schema):
    client_session_id = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=64),
    )
    mode = fields.Str(
        required=True,
        validate=validate.OneOf(["work", "short_break", "long_break"]),
    )
    planned_duration_seconds = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=43_200),
    )
    actual_duration_seconds = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=43_200),
    )
    started_at_utc = fields.AwareDateTime(required=True)
    completed_at_utc = fields.AwareDateTime(required=True)


class SessionQuerySchema(Schema):
    mode = fields.Str(
        load_default=None,
        validate=validate.OneOf(["work", "short_break", "long_break"]),
    )
    date_from = fields.Date(load_default=None)
    date_to = fields.Date(load_default=None)
    timezone = fields.Str(load_default="UTC")


class SessionListSchema(Schema):
    sessions = fields.List(fields.Nested(SessionSchema), required=True)
    total = fields.Int(required=True)


class ExportQuerySchema(Schema):
    date_from = fields.Date(load_default=None)
    date_to = fields.Date(load_default=None)
    timezone = fields.Str(load_default=None)
