from __future__ import annotations

from sqlalchemy import select

from app.extensions import db
from app.models import UserSettings


class SettingsRepository:
    def get_settings(self) -> UserSettings | None:
        stmt = select(UserSettings).limit(1)
        return db.session.execute(stmt).scalar_one_or_none()

    def save(self, settings: UserSettings) -> UserSettings:
        db.session.add(settings)
        return settings
