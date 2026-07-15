from __future__ import annotations

from datetime import datetime

from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.statistics import (
    ChartResponseSchema,
    StatisticsQuerySchema,
    StatisticsSummarySchema,
)
from app.services.settings_service import SettingsService
from app.services.statistics_service import StatisticsService
from app.time_utils import get_timezone

statistics_blp = Blueprint(
    "statistics",
    __name__,
    url_prefix="/api/statistics",
    description="Statistics endpoints",
)


def _today_in_timezone(timezone_name: str):
    zone = get_timezone(timezone_name)
    return datetime.now(zone).date()


@statistics_blp.route("/today")
class TodayStatisticsResource(MethodView):
    @statistics_blp.arguments(StatisticsQuerySchema, location="query")
    @statistics_blp.response(200, StatisticsSummarySchema)
    def get(self, query_args):
        timezone_name = (
            query_args.get("timezone") or SettingsService().get_settings().timezone
        )
        return StatisticsService().get_today_summary(
            timezone_name=timezone_name,
            current_day=_today_in_timezone(timezone_name),
        )


@statistics_blp.route("/week")
class WeekStatisticsResource(MethodView):
    @statistics_blp.arguments(StatisticsQuerySchema, location="query")
    @statistics_blp.response(200, StatisticsSummarySchema)
    def get(self, query_args):
        timezone_name = (
            query_args.get("timezone") or SettingsService().get_settings().timezone
        )
        return StatisticsService().get_week_summary(
            timezone_name=timezone_name,
            current_day=_today_in_timezone(timezone_name),
        )


@statistics_blp.route("/month")
class MonthStatisticsResource(MethodView):
    @statistics_blp.arguments(StatisticsQuerySchema, location="query")
    @statistics_blp.response(200, StatisticsSummarySchema)
    def get(self, query_args):
        timezone_name = (
            query_args.get("timezone") or SettingsService().get_settings().timezone
        )
        return StatisticsService().get_month_summary(
            timezone_name=timezone_name,
            current_day=_today_in_timezone(timezone_name),
        )


@statistics_blp.route("/chart")
class ChartStatisticsResource(MethodView):
    @statistics_blp.arguments(StatisticsQuerySchema, location="query")
    @statistics_blp.response(200, ChartResponseSchema)
    def get(self, query_args):
        timezone_name = (
            query_args.get("timezone") or SettingsService().get_settings().timezone
        )
        return StatisticsService().get_chart_data(
            timezone_name=timezone_name,
            current_day=_today_in_timezone(timezone_name),
            days=7,
        )
