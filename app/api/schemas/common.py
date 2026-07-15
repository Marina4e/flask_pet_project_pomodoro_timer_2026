from __future__ import annotations

from marshmallow import Schema, fields


class MessageSchema(Schema):
    message = fields.Str(required=True)


class HealthSchema(Schema):
    status = fields.Str(required=True)
    service = fields.Str(required=True)
    environment = fields.Str(required=True)
