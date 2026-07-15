from __future__ import annotations

from marshmallow import Schema, fields


class StatisticsQuerySchema(Schema):
    timezone = fields.Str(load_default=None)


class StatisticsSummarySchema(Schema):
    label = fields.Str(required=True)
    start_date = fields.Str(required=True)
    end_date = fields.Str(required=True)
    completed_sessions = fields.Int(required=True)
    completed_work_sessions = fields.Int(required=True)
    focus_minutes = fields.Float(required=True)
    break_minutes = fields.Float(required=True)
    total_tracked_minutes = fields.Float(required=True)


class ChartPointSchema(Schema):
    date = fields.Str(required=True)
    focus_minutes = fields.Float(required=True)
    completed_work_sessions = fields.Int(required=True)


class ChartResponseSchema(Schema):
    days = fields.List(fields.Nested(ChartPointSchema), required=True)
