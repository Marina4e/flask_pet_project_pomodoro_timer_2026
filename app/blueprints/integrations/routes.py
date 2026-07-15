from __future__ import annotations

from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.google_calendar import (
    GoogleCalendarStatusSchema,
    GoogleCalendarSyncRequestSchema,
    GoogleCalendarSyncSchema,
)
from app.services.google_calendar_service import GoogleCalendarService

integrations_blp = Blueprint(
    "integrations",
    __name__,
    url_prefix="/api/integrations/google-calendar",
    description="Google Calendar integration endpoints",
)


@integrations_blp.route("/status")
class GoogleCalendarStatusResource(MethodView):
    @integrations_blp.response(200, GoogleCalendarStatusSchema)
    def get(self):
        return GoogleCalendarService().get_status()


@integrations_blp.route("/sync")
class GoogleCalendarSyncResource(MethodView):
    @integrations_blp.arguments(GoogleCalendarSyncRequestSchema)
    @integrations_blp.response(200, GoogleCalendarSyncSchema)
    def post(self, payload):
        return GoogleCalendarService().sync_latest_work_session(payload.get("timezone"))
