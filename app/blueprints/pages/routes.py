from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, current_app, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    return render_template(
        "index.html",
        page_title="Pomodoro Work Tracker",
        current_year=datetime.now(UTC).year,
        default_timezone=current_app.config["DEFAULT_TIMEZONE"],
    )


@pages_bp.route("/statistics")
def statistics_page():
    return render_template(
        "statistics.html",
        page_title="Statistics",
        current_year=datetime.now(UTC).year,
        default_timezone=current_app.config["DEFAULT_TIMEZONE"],
    )


@pages_bp.route("/calendar")
def calendar_page():
    return render_template(
        "calendar.html",
        page_title="Calendar",
        current_year=datetime.now(UTC).year,
        default_timezone=current_app.config["DEFAULT_TIMEZONE"],
    )
