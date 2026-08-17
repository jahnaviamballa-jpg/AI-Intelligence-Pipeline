from datetime import datetime, timedelta, timezone

from src.crawlers.freshness import (
    is_fresh,
)


NOW = datetime(
    2026,
    8,
    16,
    12,
    0,
    tzinfo=timezone.utc,
)


def test_recent_item_is_fresh():

    published = NOW - timedelta(
        hours=2
    )

    assert is_fresh(
        published,
        now=NOW,
    )


def test_exactly_24_hours_is_fresh():

    published = NOW - timedelta(
        hours=24
    )

    assert is_fresh(
        published,
        now=NOW,
    )


def test_old_item_is_not_fresh():

    published = NOW - timedelta(
        hours=25
    )

    assert not is_fresh(
        published,
        now=NOW,
    )


def test_future_item_is_not_fresh():

    published = NOW + timedelta(
        minutes=5
    )

    assert not is_fresh(
        published,
        now=NOW,
    )


def test_naive_datetime_is_treated_as_utc():

    published = datetime(
        2026,
        8,
        16,
        11,
        0,
    )

    assert is_fresh(
        published,
        now=NOW,
    )