from datetime import datetime, timezone


def build_news_record(
    title: str,
    source_name: str,
    source_url: str,
    article_url: str,
    published_at: datetime,
    full_text: str,
) -> dict:
    """
    Build a source-traceable NEWS record.

    Publication time and content must come from
    the source. This function performs no inference.
    """

    if published_at.tzinfo is None:
        published_at = published_at.replace(
            tzinfo=timezone.utc
        )

    return {
        "schemaVersion": "1.0",
        "recordType": "NEWS",
        "source": {
            "name": source_name,
            "url": source_url,
        },
        "content": {
            "title": title.strip(),
            "date": published_at.astimezone(
                timezone.utc
            ).isoformat(),
            "sourceUrl": article_url,
            "fullText": full_text.strip(),
        },
        "collectedAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def build_job_record(
    company: str,
    source_name: str,
    source_url: str,
    job_url: str,
    published_at: datetime,
    is_remote: bool,
    role_family: str,
) -> dict:
    """
    Build a source-traceable JOB record.
    """

    if published_at.tzinfo is None:
        published_at = published_at.replace(
            tzinfo=timezone.utc
        )

    return {
        "schemaVersion": "1.0",
        "recordType": "JOB",
        "source": {
            "name": source_name,
            "url": source_url,
        },
        "content": {
            "company": company.strip(),
            "date": published_at.astimezone(
                timezone.utc
            ).isoformat(),
            "is_remote": is_remote,
            "role_family": role_family.strip(),
            "sourceUrl": job_url,
        },
        "collectedAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def filter_fresh_records(
    records: list[dict],
    now: datetime | None = None,
) -> list[dict]:
    """
    Keep only records whose content.date is within
    the 24-hour freshness window.

    Records with missing or invalid dates are rejected.
    """

    from src.crawlers.date_parser import (
        parse_publication_date,
    )

    from src.crawlers.freshness import (
        is_fresh,
    )

    if now is None:
        now = datetime.now(
            timezone.utc
        )

    results = []
    seen_urls = set()

    for record in records:

        content = record.get(
            "content",
            {},
        )

        source_url = content.get(
            "sourceUrl",
            "",
        )

        date_value = content.get(
            "date"
        )

        if not source_url or not date_value:
            continue

        published_at = parse_publication_date(
            date_value,
            now=now,
        )

        if published_at is None:
            continue

        if not is_fresh(
            published_at,
            now=now,
        ):
            continue

        if source_url in seen_urls:
            continue

        seen_urls.add(source_url)

        results.append(record)

    return results