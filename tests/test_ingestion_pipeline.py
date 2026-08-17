from datetime import datetime, timezone, timedelta

from src.pipeline.ingestion_pipeline import (
    deduplicate_records,
    normalize_records,
    run_ingestion,
)


def make_record(
    record_type="NEWS",
    url="https://example.com/1",
    date=None,
):
    record = {
        "schemaVersion": "1.0",
        "recordType": record_type,
        "source": {
            "name": "Test",
            "url": "https://example.com/feed",
        },
        "content": {
            "sourceUrl": url,
        },
    }

    if date is not None:
        record["content"]["date"] = date

    return record


def test_deduplicate_records():

    records = [
        make_record(url="https://example.com/1"),
        make_record(url="https://example.com/1"),
        make_record(url="https://example.com/2"),
    ]

    result = deduplicate_records(records)

    assert len(result) == 2


def test_normalize_news_applies_freshness():

    now = datetime(
        2026,
        8,
        17,
        5,
        0,
        tzinfo=timezone.utc,
    )

    fresh_date = (
        now - timedelta(hours=2)
    ).isoformat()

    old_date = (
        now - timedelta(hours=30)
    ).isoformat()

    records = [
        make_record(
            url="https://example.com/fresh",
            date=fresh_date,
        ),
        make_record(
            url="https://example.com/old",
            date=old_date,
        ),
    ]

    result = normalize_records(
        "NEWS",
        records,
        now=now,
    )

    assert len(result) == 1
    assert (
        result[0]["content"]["sourceUrl"]
        == "https://example.com/fresh"
    )


def test_startups_do_not_use_24_hour_filter():

    records = [
        make_record(
            record_type="STARTUP",
            url="https://example.com/startup",
        )
    ]

    result = normalize_records(
        "STARTUP",
        records,
    )

    assert len(result) == 1


def test_run_ingestion_combines_sources():

    sources = {
        "NEWS": lambda: [
            make_record(
                url="https://example.com/news"
            )
        ],
        "STARTUP": lambda: [
            make_record(
                record_type="STARTUP",
                url="https://example.com/startup",
            )
        ],
    }

    result = run_ingestion(sources)

    assert len(result) == 2


def test_run_ingestion_isolates_source_failure():

    def broken_source():
        raise RuntimeError("source unavailable")

    sources = {
        "NEWS": broken_source,
        "STARTUP": lambda: [
            make_record(
                record_type="STARTUP",
                url="https://example.com/startup",
            )
        ],
    }

    result = run_ingestion(sources)

    assert len(result) == 1
    assert (
        result[0]["recordType"]
        == "STARTUP"
    )