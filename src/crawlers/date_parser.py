import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime


RELATIVE_PATTERN = re.compile(
    r"^\s*(\d+)\s+"
    r"(minute|minutes|hour|hours|day|days)"
    r"\s+ago\s*$",
    re.IGNORECASE,
)


def parse_relative_date(
    value: str,
    now: datetime,
) -> datetime | None:

    match = RELATIVE_PATTERN.match(
        value
    )

    if not match:
        return None

    amount = int(
        match.group(1)
    )

    unit = match.group(2).lower()

    if unit.startswith("minute"):
        delta = timedelta(
            minutes=amount
        )

    elif unit.startswith("hour"):
        delta = timedelta(
            hours=amount
        )

    else:
        delta = timedelta(
            days=amount
        )

    return now - delta


def parse_publication_date(
    value: str | None,
    now: datetime | None = None,
) -> datetime | None:
    """
    Parse common publication date formats
    into timezone-aware UTC datetime.
    """

    if not value:
        return None

    if now is None:
        now = datetime.now(
            timezone.utc
        )

    if now.tzinfo is None:
        now = now.replace(
            tzinfo=timezone.utc
        )

    value = value.strip()

    relative = parse_relative_date(
        value,
        now,
    )

    if relative:
        return relative

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except ValueError:
        pass

    try:
        parsed = parsedate_to_datetime(
            value
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except (TypeError, ValueError):
        return None