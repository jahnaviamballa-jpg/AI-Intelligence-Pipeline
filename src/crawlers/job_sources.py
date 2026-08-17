from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from src.crawlers.signal_sources import build_job_record


def parse_job_date(entry) -> datetime | None:
    """Extract a source-provided publication date."""

    for field in ("published", "updated", "created"):
        value = entry.get(field)

        if not value:
            continue

        try:
            parsed = parsedate_to_datetime(value)

            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return parsed.astimezone(timezone.utc)

        except (TypeError, ValueError, OverflowError):
            continue

    return None


def infer_remote(entry) -> bool:
    """
    Detect explicit remote wording from the source entry.

    This is deliberately conservative.
    """

    text = " ".join(
        [
            entry.get("title", ""),
            entry.get("summary", ""),
            entry.get("description", ""),
        ]
    ).lower()

    remote_terms = (
        "remote",
        "work from home",
        "work-from-home",
    )

    return any(
        term in text
        for term in remote_terms
    )


def extract_role_family(title: str) -> str:
    """
    Normalize a job title into a simple role family.

    This does not use an LLM and does not invent roles.
    """

    title_lower = title.lower()

    if "machine learning" in title_lower:
        return "Machine Learning"

    if "artificial intelligence" in title_lower:
        return "Artificial Intelligence"

    if "ai engineer" in title_lower:
        return "AI Engineering"

    if "data scientist" in title_lower:
        return "Data Science"

    if "software engineer" in title_lower:
        return "Software Engineering"

    if "developer" in title_lower:
        return "Software Development"

    return title.strip()


def extract_jobs_from_feed(
    feed_url: str,
    source_name: str,
) -> list[dict]:
    """
    Extract source-traceable JOB records from an RSS/Atom feed.
    """

    feed = feedparser.parse(feed_url)

    records = []

    for entry in feed.entries:

        title = entry.get(
            "title",
            "",
        ).strip()

        job_url = entry.get(
            "link",
            "",
        ).strip()

        published_at = parse_job_date(
            entry
        )

        if (
            not title
            or not job_url
            or not published_at
        ):
            continue

        company = (
            entry.get(
                "author",
                "",
            ).strip()
            or source_name
        )

        records.append(
            build_job_record(
                company=company,
                source_name=source_name,
                source_url=feed_url,
                job_url=job_url,
                published_at=published_at,
                is_remote=infer_remote(entry),
                role_family=extract_role_family(
                    title
                ),
            )
        )

    return records