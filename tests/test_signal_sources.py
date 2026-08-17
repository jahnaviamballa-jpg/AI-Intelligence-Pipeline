from datetime import datetime, timedelta, timezone

from src.crawlers.signal_sources import (
    build_job_record,
    build_news_record,
    filter_fresh_records,
)


NOW = datetime(
    2026,
    8,
    16,
    12,
    0,
    tzinfo=timezone.utc,
)


def test_build_news_record():

    record = build_news_record(
        title="AI News",
        source_name="Example News",
        source_url="https://example.com",
        article_url="https://example.com/news/1",
        published_at=NOW,
        full_text="Article content.",
    )

    assert record["recordType"] == "NEWS"
    assert record["content"]["title"] == "AI News"


def test_build_job_record():

    record = build_job_record(
        company="Example AI",
        source_name="Example Jobs",
        source_url="https://example.com/jobs",
        job_url="https://example.com/jobs/1",
        published_at=NOW,
        is_remote=True,
        role_family="Engineering",
    )

    assert record["recordType"] == "JOB"
    assert record["content"]["company"] == "Example AI"


def test_filter_fresh_records():

    records = [
        {
            "recordType": "NEWS",
            "content": {
                "sourceUrl": "https://example.com/1",
                "date": (
                    NOW - timedelta(hours=2)
                ).isoformat(),
            },
        },
        {
            "recordType": "NEWS",
            "content": {
                "sourceUrl": "https://example.com/2",
                "date": (
                    NOW - timedelta(hours=30)
                ).isoformat(),
            },
        },
    ]

    result = filter_fresh_records(
        records,
        now=NOW,
    )

    assert len(result) == 1
    assert (
        result[0]["content"]["sourceUrl"]
        == "https://example.com/1"
    )


def test_invalid_date_is_rejected():

    records = [
        {
            "recordType": "NEWS",
            "content": {
                "sourceUrl": "https://example.com/1",
                "date": "unknown",
            },
        }
    ]

    result = filter_fresh_records(
        records,
        now=NOW,
    )

    assert result == []


def test_duplicate_url_is_removed():

    fresh_date = (
        NOW - timedelta(hours=1)
    ).isoformat()

    records = [
        {
            "recordType": "NEWS",
            "content": {
                "sourceUrl": "https://example.com/1",
                "date": fresh_date,
            },
        },
        {
            "recordType": "NEWS",
            "content": {
                "sourceUrl": "https://example.com/1",
                "date": fresh_date,
            },
        },
    ]

    result = filter_fresh_records(
        records,
        now=NOW,
    )

    assert len(result) == 1