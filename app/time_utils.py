from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.errors import ValidationAppError


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def parse_datetime_value(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value

    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationAppError(
            "Invalid datetime value",
            details={"value": value},
        ) from exc


def to_storage_utc(value: datetime | str) -> datetime:
    """Зберігаємо naive datetime, але трактуємо його як UTC."""

    return ensure_utc(parse_datetime_value(value)).replace(tzinfo=None)


def from_storage_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def utc_isoformat(value: datetime) -> str:
    return from_storage_utc(value).isoformat().replace("+00:00", "Z")


def get_timezone(timezone_name: str) -> ZoneInfo:
    normalized_name = str(timezone_name).strip()
    if not normalized_name:
        raise ValidationAppError(
            "Invalid time zone",
            details={"timezone": timezone_name},
        )
    try:
        return ZoneInfo(normalized_name)
    except ZoneInfoNotFoundError as exc:
        raise ValidationAppError(
            "Invalid time zone",
            details={"timezone": timezone_name},
        ) from exc


def local_date_to_utc_range(day: date, timezone_name: str) -> tuple[datetime, datetime]:
    zone = get_timezone(timezone_name)
    start_local = datetime.combine(day, time.min, tzinfo=zone)
    end_local = start_local + timedelta(days=1)
    return to_storage_utc(start_local), to_storage_utc(end_local)


def local_range_to_utc_range(
    start_day: date, end_day_exclusive: date, timezone_name: str
) -> tuple[datetime, datetime]:
    zone = get_timezone(timezone_name)
    start_local = datetime.combine(start_day, time.min, tzinfo=zone)
    end_local = datetime.combine(end_day_exclusive, time.min, tzinfo=zone)
    return to_storage_utc(start_local), to_storage_utc(end_local)


def to_local_datetime(value: datetime, timezone_name: str) -> datetime:
    zone = get_timezone(timezone_name)
    return from_storage_utc(value).astimezone(zone)
