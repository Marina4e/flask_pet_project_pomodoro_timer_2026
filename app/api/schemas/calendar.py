from __future__ import annotations

from marshmallow import Schema, fields, validate


class CalendarMonthQuerySchema(Schema):
    year = fields.Int(required=True, validate=validate.Range(min=2000, max=2100))
    month = fields.Int(required=True, validate=validate.Range(min=1, max=12))
    timezone = fields.Str(required=True)


class CalendarDayQuerySchema(Schema):
    date = fields.Date(required=True)
    timezone = fields.Str(required=True)


class CalendarDaySchema(Schema):
    date = fields.Str(required=True)
    session_count = fields.Int(required=True)
    completed_work_sessions = fields.Int(required=True)
    focus_minutes = fields.Float(required=True)
    has_activity = fields.Bool(required=True)


class CalendarMonthSchema(Schema):
    year = fields.Int(required=True)
    month = fields.Int(required=True)
    days = fields.List(fields.Nested(CalendarDaySchema), required=True)


class CalendarDetailSessionSchema(Schema):
    id = fields.Int(required=True)
    client_session_id = fields.Str(required=True)
    mode = fields.Str(required=True)
    actual_duration_seconds = fields.Int(required=True)
    started_at_local = fields.Str(required=True)
    completed_at_local = fields.Str(required=True)


class CalendarDayDetailsSchema(Schema):
    date = fields.Str(required=True)
    timezone = fields.Str(required=True)
    total_sessions = fields.Int(required=True)
    completed_work_sessions = fields.Int(required=True)
    focus_minutes = fields.Float(required=True)
    sessions = fields.List(fields.Nested(CalendarDetailSessionSchema), required=True)
