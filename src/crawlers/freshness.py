from datetime import datetime, timedelta, timezone


def ensure_utc(value: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    Naive datetimes are treated as UTC.
    """

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    )


def is_fresh(
    published_at: datetime,
    now: datetime | None = None,
    max_age_hours: int = 24,
) -> bool:
    """
    Return True only when the publication time is
    within the configured freshness window.
    """

    published_at = ensure_utc(
        published_at
    )

    if now is None:
        now = datetime.now(
            timezone.utc
        )
    else:
        now = ensure_utc(now)

    age = now - published_at

    return (
        timedelta(0)
        <= age
        <= timedelta(
            hours=max_age_hours
        )
    )