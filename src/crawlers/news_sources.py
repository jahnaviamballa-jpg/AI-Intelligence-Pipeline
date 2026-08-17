from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from src.crawlers.signal_sources import build_news_record


def parse_feed_date(entry) -> datetime | None:
    """
    Extract a publication timestamp from an RSS/Atom entry.
    """
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


def extract_news_from_feed(
    feed_url: str,
    source_name: str,
) -> list[dict]:
    """
    Extract source-traceable news records from RSS/Atom.

    No publication dates or entities are invented.
    Entries without a valid source date are skipped.
    """

    feed = feedparser.parse(feed_url)

    records = []

    for entry in feed.entries:

        title = entry.get("title", "").strip()
        article_url = entry.get("link", "").strip()

        published_at = parse_feed_date(entry)

        if not title or not article_url or not published_at:
            continue

        full_text = (
            entry.get("summary")
            or entry.get("description")
            or ""
        )

        records.append(
            build_news_record(
                title=title,
                source_name=source_name,
                source_url=feed_url,
                article_url=article_url,
                published_at=published_at,
                full_text=full_text,
            )
        )

    return records


NEWS_SOURCES = {
    "TechCrunch AI": (
        "https://techcrunch.com/category/artificial-intelligence/feed/"
    ),
    "MIT Technology Review": (
        "https://www.technologyreview.com/feed/"
    ),
    "VentureBeat AI": (
        "https://venturebeat.com/category/ai/feed/"
    ),
}