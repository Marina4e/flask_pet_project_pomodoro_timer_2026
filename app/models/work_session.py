from __future__ import annotations

from app.extensions import db
from app.time_utils import utc_now


class WorkSession(db.Model):
    __tablename__ = "work_sessions"
    __table_args__ = (
        db.UniqueConstraint(
            "client_session_id",
            name="uq_work_sessions_client_session_id",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    client_session_id = db.Column(db.String(64), nullable=False, unique=True)
    mode = db.Column(db.String(20), nullable=False, index=True)
    planned_duration_seconds = db.Column(db.Integer, nullable=False)
    actual_duration_seconds = db.Column(db.Integer, nullable=False)
    started_at_utc = db.Column(db.DateTime, nullable=False, index=True)
    completed_at_utc = db.Column(db.DateTime, nullable=False, index=True)
    google_calendar_event_id = db.Column(db.String(255), nullable=True, unique=True)
    created_at_utc = db.Column(db.DateTime, nullable=False, default=utc_now)

    def __repr__(self) -> str:
        return (
            f"<WorkSession id={self.id} mode={self.mode} "
            f"completed_at_utc={self.completed_at_utc}>"
        )
