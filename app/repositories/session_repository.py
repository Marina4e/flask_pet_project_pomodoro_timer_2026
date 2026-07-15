from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.extensions import db
from app.models import WorkSession


class SessionRepository:
    def add(self, session: WorkSession) -> WorkSession:
        db.session.add(session)
        return session

    def get_by_client_session_id(self, client_session_id: str) -> WorkSession | None:
        stmt = select(WorkSession).where(
            WorkSession.client_session_id == client_session_id
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, session_id: int) -> WorkSession | None:
        return db.session.get(WorkSession, session_id)

    def list_sessions(
        self,
        *,
        mode: str | None = None,
        start_utc: datetime | None = None,
        end_utc: datetime | None = None,
    ) -> list[WorkSession]:
        stmt = select(WorkSession).order_by(WorkSession.completed_at_utc.desc())

        if mode:
            stmt = stmt.where(WorkSession.mode == mode)
        if start_utc:
            stmt = stmt.where(WorkSession.completed_at_utc >= start_utc)
        if end_utc:
            stmt = stmt.where(WorkSession.completed_at_utc < end_utc)

        return list(db.session.execute(stmt).scalars())

    def get_completed_between(
        self, start_utc: datetime, end_utc: datetime
    ) -> list[WorkSession]:
        return self.list_sessions(start_utc=start_utc, end_utc=end_utc)

    def get_latest_work_session(self) -> WorkSession | None:
        stmt = (
            select(WorkSession)
            .where(WorkSession.mode == "work")
            .order_by(WorkSession.completed_at_utc.desc())
            .limit(1)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def delete(self, session: WorkSession) -> None:
        db.session.delete(session)
