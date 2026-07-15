from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.errors import ConflictAppError, NotFoundAppError, ValidationAppError
from app.extensions import db
from app.models import WorkSession
from app.repositories import SessionRepository
from app.services.pomodoro_timer import ALLOWED_TIMER_MODES
from app.time_utils import (
    local_date_to_utc_range,
    local_range_to_utc_range,
    to_storage_utc,
    utc_isoformat,
)


class SessionService:
    def __init__(self, repository: SessionRepository | None = None) -> None:
        self.repository = repository or SessionRepository()

    def create_session(self, payload: dict[str, object]) -> dict[str, object]:
        mode = str(payload["mode"])
        client_session_id = str(payload["client_session_id"]).strip()
        planned_duration_seconds = int(payload["planned_duration_seconds"])
        actual_duration_seconds = int(payload["actual_duration_seconds"])

        if mode not in ALLOWED_TIMER_MODES:
            raise ValidationAppError("Unsupported session mode", details={"mode": mode})
        if not client_session_id:
            raise ValidationAppError("client_session_id is required")
        if planned_duration_seconds <= 0 or actual_duration_seconds <= 0:
            raise ValidationAppError("Session duration must be greater than zero")

        started_at = to_storage_utc(payload["started_at_utc"])  # type: ignore[arg-type]
        completed_at = to_storage_utc(payload["completed_at_utc"])  # type: ignore[arg-type]

        if completed_at <= started_at:
            raise ValidationAppError(
                "completed_at_utc must be later than started_at_utc"
            )

        existing = self.repository.get_by_client_session_id(client_session_id)
        if existing is not None:
            raise ConflictAppError(
                "Session with this client_session_id already exists",
                details={"client_session_id": client_session_id},
            )

        session = WorkSession(
            client_session_id=client_session_id,
            mode=mode,
            planned_duration_seconds=planned_duration_seconds,
            actual_duration_seconds=actual_duration_seconds,
            started_at_utc=started_at,
            completed_at_utc=completed_at,
        )

        try:
            self.repository.add(session)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictAppError(
                "Duplicate session detected",
                details={"client_session_id": client_session_id},
            ) from exc
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise ValidationAppError("Unable to save session") from exc

        return self.serialize(session)

    def list_sessions(self, query_args: dict[str, object]) -> dict[str, object]:
        mode = str(query_args["mode"]) if query_args.get("mode") else None
        timezone_name = str(query_args.get("timezone") or "UTC")
        date_from = query_args.get("date_from")
        date_to = query_args.get("date_to")

        start_utc = end_utc = None
        if isinstance(date_from, date):
            end_date = date_to if isinstance(date_to, date) else date_from
            if end_date < date_from:
                raise ValidationAppError(
                    "date_to must not be earlier than date_from",
                    details={
                        "date_from": date_from.isoformat(),
                        "date_to": end_date.isoformat(),
                    },
                )
            start_utc, end_utc = local_range_to_utc_range(
                date_from,
                end_date + timedelta(days=1),
                timezone_name,
            )

        sessions = self.repository.list_sessions(
            mode=mode,
            start_utc=start_utc,
            end_utc=end_utc,
        )
        return {
            "sessions": [self.serialize(item) for item in sessions],
            "total": len(sessions),
        }

    def get_session(self, session_id: int) -> dict[str, object]:
        session = self.repository.get_by_id(session_id)
        if session is None:
            raise NotFoundAppError(
                "Session not found", details={"session_id": session_id}
            )
        return self.serialize(session)

    def delete_session(self, session_id: int) -> dict[str, str]:
        session = self.repository.get_by_id(session_id)
        if session is None:
            raise NotFoundAppError(
                "Session not found", details={"session_id": session_id}
            )

        self.repository.delete(session)
        db.session.commit()
        return {"message": "Session deleted"}

    def list_sessions_for_day(self, day: date, timezone_name: str) -> list[WorkSession]:
        start_utc, end_utc = local_date_to_utc_range(day, timezone_name)
        return self.repository.get_completed_between(start_utc, end_utc)

    @staticmethod
    def serialize(session: WorkSession) -> dict[str, object]:
        return {
            "id": session.id,
            "client_session_id": session.client_session_id,
            "mode": session.mode,
            "planned_duration_seconds": session.planned_duration_seconds,
            "actual_duration_seconds": session.actual_duration_seconds,
            "started_at_utc": utc_isoformat(session.started_at_utc),
            "completed_at_utc": utc_isoformat(session.completed_at_utc),
            "google_calendar_event_id": session.google_calendar_event_id,
            "created_at_utc": utc_isoformat(session.created_at_utc),
        }
