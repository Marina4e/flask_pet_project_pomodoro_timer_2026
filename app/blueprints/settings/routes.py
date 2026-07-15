from __future__ import annotations

from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.settings import SettingsSchema, SettingsUpdateSchema
from app.services.settings_service import SettingsService

settings_blp = Blueprint(
    "settings",
    __name__,
    url_prefix="/api/settings",
    description="Application settings endpoints",
)


@settings_blp.route("")
class SettingsResource(MethodView):
    @settings_blp.response(200, SettingsSchema)
    def get(self):
        return SettingsService().get_settings_payload()

    @settings_blp.arguments(SettingsUpdateSchema)
    @settings_blp.response(200, SettingsSchema)
    def put(self, payload):
        return SettingsService().update_settings(payload)
