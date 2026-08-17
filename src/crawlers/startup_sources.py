from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup


YC_COMPANIES_URL = "https://www.ycombinator.com/companies"


def normalize_text(value: str) -> str:
    return " ".join(value.split()).strip()


def build_startup_record(
    name: str,
    source_url: str,
    company_url: str,
    employee_count: int | None = None,
) -> dict:
    """
    Build one startup record.

    Values are source-derived. Missing values remain None.
    """

    return {
        "schemaVersion": "1.0",
        "recordType": "STARTUP",
        "source": {
            "name": "Y Combinator",
            "url": source_url,
        },
        "content": {
            "entityName": name,
            "data": {
                "employeeCount": employee_count,
            },
            "sourceUrl": company_url,
        },
        "collectedAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def extract_yc_startups(
    html: str,
    source_url: str = YC_COMPANIES_URL,
) -> list[dict]:
    """
    Extract startup records from YC company-directory HTML.

    This intentionally extracts only links that clearly
    belong to the YC company directory. It does not infer
    companies from arbitrary text.
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

        url = urljoin(
            source_url,
            href,
        )

        parsed_path = url.split(
            "ycombinator.com",
            1,
        )[-1]

        if not parsed_path.startswith(
            "/companies/"
        ):
            continue

        name = normalize_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        )

        if not name:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        records.append(
            build_startup_record(
                name=name,
                source_url=source_url,
                company_url=url,
            )
        )

    return records


def filter_candidate_startups(
    records: list[dict],
) -> list[dict]:
    """
    Remove malformed and duplicate startup records.
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
                "entityName",
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