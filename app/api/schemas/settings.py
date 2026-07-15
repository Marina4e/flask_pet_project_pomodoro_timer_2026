from __future__ import annotations

from marshmallow import Schema, fields, validate


class SettingsSchema(Schema):
    work_duration_minutes = fields.Int(required=True)
    short_break_minutes = fields.Int(required=True)
    long_break_minutes = fields.Int(required=True)
    cycles_before_long_break = fields.Int(required=True)
    sound_enabled = fields.Bool(required=True)
    auto_start_next_session = fields.Bool(required=True)
    theme = fields.Str(required=True)
    timezone = fields.Str(required=True)
    test_mode_enabled = fields.Bool(required=True)


class SettingsUpdateSchema(Schema):
    work_duration_minutes = fields.Int(
        required=True,
        validate=validate.OneOf([15, 25, 30, 45, 60]),
    )
    short_break_minutes = fields.Int(
        required=True,
        validate=validate.OneOf([5, 10, 15]),
    )
    long_break_minutes = fields.Int(
        required=True,
        validate=validate.OneOf([5, 10, 15]),
    )
    cycles_before_long_break = fields.Int(
        required=True,
        validate=validate.Range(min=2, max=12),
    )
    sound_enabled = fields.Bool(required=True)
    auto_start_next_session = fields.Bool(required=True)
    theme = fields.Str(
        required=True,
        validate=validate.OneOf(["light", "dark", "system"]),
    )
    timezone = fields.Str(required=True)
