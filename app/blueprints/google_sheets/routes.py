from __future__ import annotations

from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.google_sheets import (
    GoogleSheetsSettingsSchema,
    GoogleSheetsSettingsUpdateSchema,
    GoogleSheetsSyncSchema,
)
from app.services.google_sheets_service import GoogleSheetsService

google_sheets_blp = Blueprint(
    "google_sheets",
    __name__,
    url_prefix="/api/integrations/google-sheets",
    description="Google Sheets integration endpoints",
)


@google_sheets_blp.route("/settings")
class GoogleSheetsSettingsResource(MethodView):
    @google_sheets_blp.response(200, GoogleSheetsSettingsSchema)
    def get(self):
        return GoogleSheetsService().get_settings_payload()

    @google_sheets_blp.arguments(GoogleSheetsSettingsUpdateSchema)
    @google_sheets_blp.response(200, GoogleSheetsSettingsSchema)
    def put(self, payload):
        return GoogleSheetsService().update_settings(payload)


@google_sheets_blp.route("/sync")
class GoogleSheetsSyncResource(MethodView):
    @google_sheets_blp.response(200, GoogleSheetsSyncSchema)
    def post(self):
        return GoogleSheetsService().sync_completed_sessions()
