from __future__ import annotations

from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.common import HealthSchema

health_blp = Blueprint(
    "health",
    __name__,
    url_prefix="/api/health",
    description="Service health checks",
)


@health_blp.route("")
class HealthResource(MethodView):
    @health_blp.response(200, HealthSchema)
    def get(self):
        return {
            "status": "ok",
            "service": "pomodoro-work-tracker",
            "environment": current_app.config["ENV_NAME"],
        }
