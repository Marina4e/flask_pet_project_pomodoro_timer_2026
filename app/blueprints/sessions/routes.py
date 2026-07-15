from __future__ import annotations

from flask.views import MethodView
from flask_smorest import Blueprint

from app.api.schemas.common import MessageSchema
from app.api.schemas.session import (
    SessionCreateSchema,
    SessionListSchema,
    SessionQuerySchema,
    SessionSchema,
)
from app.services.session_service import SessionService

sessions_blp = Blueprint(
    "sessions",
    __name__,
    url_prefix="/api/sessions",
    description="Completed session management",
)


@sessions_blp.route("")
class SessionCollectionResource(MethodView):
    @sessions_blp.arguments(SessionCreateSchema)
    @sessions_blp.response(201, SessionSchema)
    def post(self, payload):
        return SessionService().create_session(payload)

    @sessions_blp.arguments(SessionQuerySchema, location="query")
    @sessions_blp.response(200, SessionListSchema)
    def get(self, query_args):
        return SessionService().list_sessions(query_args)


@sessions_blp.route("/<int:session_id>")
class SessionResource(MethodView):
    @sessions_blp.response(200, SessionSchema)
    def get(self, session_id: int):
        return SessionService().get_session(session_id)

    @sessions_blp.response(200, MessageSchema)
    def delete(self, session_id: int):
        return SessionService().delete_session(session_id)
