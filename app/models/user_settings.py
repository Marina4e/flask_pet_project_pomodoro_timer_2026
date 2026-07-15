from __future__ import annotations

from app.extensions import db
from app.time_utils import utc_now


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True, default=1)
    work_duration_minutes = db.Column(db.Integer, nullable=False)
    short_break_minutes = db.Column(db.Integer, nullable=False)
    long_break_minutes = db.Column(db.Integer, nullable=False)
    cycles_before_long_break = db.Column(db.Integer, nullable=False, default=4)
    sound_enabled = db.Column(db.Boolean, nullable=False, default=True)
    auto_start_next_session = db.Column(db.Boolean, nullable=False, default=True)
    theme = db.Column(db.String(16), nullable=False, default="system")
    timezone = db.Column(db.String(64), nullable=False)
    google_sheets_enabled = db.Column(db.Boolean, nullable=True)
    google_sheets_spreadsheet_id = db.Column(db.String(255), nullable=True)
    updated_at_utc = db.Column(
        db.DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    def __repr__(self) -> str:
        return f"<UserSettings theme={self.theme} timezone={self.timezone}>"
