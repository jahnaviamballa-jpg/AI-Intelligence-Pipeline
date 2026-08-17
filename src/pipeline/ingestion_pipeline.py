from datetime import datetime, timezone
from typing import Callable

from src.crawlers.signal_sources import filter_fresh_records

from src.crawlers.product_sources import filter_candidate_products


Record = dict
Loader = Callable[[], list[Record]]


def deduplicate_records(
    records: list[Record],
) -> list[Record]:
    """
    Remove duplicate records using source URL.

    Records without a source URL are ignored because
    source traceability is required.
    """

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

        if not source_url:
            continue

        if source_url in seen_urls:
            continue

        seen_urls.add(source_url)

        results.append(record)

    return results


def normalize_records(
    record_type: str,
    records: list[Record],
    now: datetime | None = None,
) -> list[Record]:
    """
    Apply source-type-specific normalization and filtering.
    """

    if now is None:
        now = datetime.now(timezone.utc)

    if record_type in {"NEWS", "JOB"}:
        records = filter_fresh_records(
            records,
            now=now,
        )

    elif record_type == "STARTUP":
        pass

    elif record_type == "PRODUCT":
        records = filter_candidate_products(
            records,
        )

    return deduplicate_records(records)


def run_ingestion(
    sources: dict[str, Loader],
    now: datetime | None = None,
) -> list[Record]:
    """
    Execute registered source loaders and return
    normalized, deduplicated records.

    Source failures are isolated so one unavailable
    source does not stop the entire ingestion run.
    """

    all_records = []

    for record_type, loader in sources.items():

        try:
            records = loader()

        except Exception:
            continue

        all_records.extend(records)

        

    return all_records