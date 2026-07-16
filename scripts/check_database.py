from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_database_path() -> Path:
    raw_database_url = os.getenv("DATABASE_URL", "sqlite:///pomodoro.db")
    if not raw_database_url.startswith("sqlite:///"):
        raise SystemExit("check_database.py supports only SQLite DATABASE_URL values.")

    sqlite_target = raw_database_url.removeprefix("sqlite:///")
    if not sqlite_target or sqlite_target == ":memory:":
        raise SystemExit("A file-based SQLite database is required for this check.")

    database_path = Path(sqlite_target)
    if database_path.is_absolute():
        return database_path

    return (PROJECT_ROOT / "instance" / database_path).resolve()


def fetch_table_names(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return [row[0] for row in rows]


def work_session_columns(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("PRAGMA table_info(work_sessions)").fetchall()
    return {row[1] for row in rows}


def print_report(connection: sqlite3.Connection, database_path: Path) -> None:
    tables = fetch_table_names(connection)
    print(f"Database path: {database_path}")
    print(f"Tables: {', '.join(tables) if tables else '(none)'}")

    if "work_sessions" not in tables:
        print("Work sessions count: unavailable (work_sessions table is missing)")
        return

    session_columns = work_session_columns(connection)
    sync_column = (
        "google_calendar_event_id"
        if "google_calendar_event_id" in session_columns
        else "NULL AS google_calendar_event_id"
    )
    total_sessions = connection.execute(
        "SELECT COUNT(*) FROM work_sessions"
    ).fetchone()[0]
    rows = connection.execute(
        f"""
        SELECT
            id,
            client_session_id,
            started_at_utc,
            completed_at_utc,
            actual_duration_seconds,
            mode,
            {sync_column}
        FROM work_sessions
        ORDER BY completed_at_utc DESC
        LIMIT 10
        """
    ).fetchall()

    print(f"Work sessions count: {total_sessions}")
    print()
    print("Recent sessions:")

    if not rows:
        print("- No saved sessions found.")
        return

    for (
        session_id,
        client_session_id,
        started_at,
        completed_at,
        duration_seconds,
        mode,
        calendar_event_id,
    ) in rows:
        sync_status = "synced" if calendar_event_id else "not_synced"
        print(
            f"- id={session_id} | client_session_id={client_session_id} | "
            f"start={started_at} | end={completed_at} | "
            f"duration_seconds={duration_seconds} | mode={mode} | "
            f"status=completed | google_calendar={sync_status}"
        )


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    database_path = resolve_database_path()
    if not database_path.exists():
        print(f"Database file does not exist yet: {database_path}")
        return 1

    connection = sqlite3.connect(database_path)
    try:
        print_report(connection, database_path)
    finally:
        connection.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
