from __future__ import annotations

from marshmallow import Schema, fields


class GoogleSheetsSettingsSchema(Schema):
    enabled = fields.Bool(required=True)
    spreadsheet_id = fields.Str(required=True)
    credentials_configured = fields.Bool(required=True)


class GoogleSheetsSettingsUpdateSchema(Schema):
    enabled = fields.Bool(required=True)
    spreadsheet_id = fields.Str(required=True)


class GoogleSheetsSyncSchema(Schema):
    status = fields.Str(required=True)
    spreadsheet_id = fields.Str(required=True)
    exported = fields.Int(required=True)
    skipped = fields.Int(required=True)
    total_completed_work_sessions = fields.Int(required=True)
    message = fields.Str(required=True)
