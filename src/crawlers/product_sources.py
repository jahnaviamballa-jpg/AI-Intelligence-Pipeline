from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def normalize_text(value: str) -> str:
    return " ".join(value.split()).strip()


def build_product_record(
    name: str,
    source_name: str,
    source_url: str,
    product_url: str,
    startup_name: str | None = None,
    pricing_model: str | None = None,
) -> dict:
    """
    Build one source-traceable product record.

    No values are inferred when the source does not
    explicitly provide them.
    """

    return {
        "schemaVersion": "1.0",
        "recordType": "PRODUCT",
        "source": {
            "name": source_name,
            "url": source_url,
        },
        "content": {
            "productName": name,
            "startupName": startup_name,
            "pricingModel": pricing_model,
            "sourceUrl": product_url,
        },
        "collectedAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def extract_product_links(
    html: str,
    base_url: str,
    source_name: str,
) -> list[dict]:
    """
    Extract product records only from explicit links
    present in the source HTML.

    The adapter does not invent product names.
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    records = []
    seen_urls = set()

    for anchor in soup.find_all(
        "a",
        href=True,
    ):

        href = anchor.get(
            "href",
            "",
        ).strip()

        if not href:
            continue

        product_url = urljoin(
            base_url,
            href,
        )

        name = normalize_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        )

        if not name:
            continue

        if product_url in seen_urls:
            continue

        seen_urls.add(product_url)

        records.append(
            build_product_record(
                name=name,
                source_name=source_name,
                source_url=base_url,
                product_url=product_url,
            )
        )

    return records


def filter_candidate_products(
    records: list[dict],
) -> list[dict]:
    """
    Remove malformed and duplicate products.
    """

    results = []
    seen_names = set()

    for record in records:

        content = record.get(
            "content",
            {},
        )

        name = normalize_text(
            content.get(
                "productName",
                "",
            )
        )

        source_url = content.get(
            "sourceUrl",
            "",
        )

        if not name or not source_url:
            continue

        key = name.casefold()

        if key in seen_names:
            continue

        seen_names.add(key)

        results.append(record)

    return results