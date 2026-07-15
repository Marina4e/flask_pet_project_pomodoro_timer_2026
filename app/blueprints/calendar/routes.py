from __future__ import annotations

from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.calendar import (
    CalendarDayDetailsSchema,
    CalendarDayQuerySchema,
    CalendarMonthQuerySchema,
    CalendarMonthSchema,
)
from app.services.calendar_service import CalendarService

calendar_blp = Blueprint(
    "calendar",
    __name__,
    url_prefix="/api/calendar",
    description="Calendar and day-detail endpoints",
)


@calendar_blp.route("/month")
class CalendarMonthResource(MethodView):
    @calendar_blp.arguments(CalendarMonthQuerySchema, location="query")
    @calendar_blp.response(200, CalendarMonthSchema)
    def get(self, query_args):
        return CalendarService().get_month_summary(
            year=int(query_args["year"]),
            month=int(query_args["month"]),
            timezone_name=str(query_args["timezone"]),
        )


@calendar_blp.route("/day")
class CalendarDayResource(MethodView):
    @calendar_blp.arguments(CalendarDayQuerySchema, location="query")
    @calendar_blp.response(200, CalendarDayDetailsSchema)
    def get(self, query_args):
        return CalendarService().get_day_details(
            selected_day=query_args["date"],
            timezone_name=str(query_args["timezone"]),
        )
