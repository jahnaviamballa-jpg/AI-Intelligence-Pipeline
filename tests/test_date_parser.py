from datetime import datetime, timezone

from src.crawlers.date_parser import (
    parse_publication_date,
)


NOW = datetime(
    2026,
    8,
    16,
    12,
    0,
    tzinfo=timezone.utc,
)


def test_parse_hours_ago():

    result = parse_publication_date(
        "2 hours ago",
        now=NOW,
    )

    assert result == datetime(
        2026,
        8,
        16,
        10,
        0,
        tzinfo=timezone.utc,
    )


def test_parse_days_ago():

    result = parse_publication_date(
        "1 day ago",
        now=NOW,
    )

    assert result == datetime(
        2026,
        8,
        15,
        12,
        0,
        tzinfo=timezone.utc,
    )


def test_parse_iso_timestamp():

    result = parse_publication_date(
        "2026-08-16T10:30:00Z",
        now=NOW,
    )

    assert result == datetime(
        2026,
        8,
        16,
        10,
        30,
        tzinfo=timezone.utc,
    )


def test_parse_rfc_timestamp():

    result = parse_publication_date(
        "Sun, 16 Aug 2026 10:30:00 GMT",
        now=NOW,
    )

    assert result == datetime(
        2026,
        8,
        16,
        10,
        30,
        tzinfo=timezone.utc,
    )


def test_missing_date():

    assert (
        parse_publication_date(
            None,
            now=NOW,
        )
        is None
    )


def test_invalid_date():

    assert (
        parse_publication_date(
            "not a date",
            now=NOW,
        )
        is None
    )