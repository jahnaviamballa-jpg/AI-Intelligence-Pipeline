import asyncio
import json
import ssl
from pathlib import Path
from typing import Any

import aiohttp
import certifi


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/research_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/enriched_research_papers.json"
)

ARXIV_PAGE_TIMEOUT = 20

MAX_CONCURRENT_REQUESTS = 10

USER_AGENT = "AI-Intelligence-Pipeline/1.0"


# =========================================================
# SSL
# =========================================================

def create_ssl_context():

    return ssl.create_default_context(
        cafile=certifi.where()
    )


# =========================================================
# Load Day 1 dataset
# =========================================================

def load_papers() -> list[dict[str, Any]]:

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):

        raise ValueError(
            "Expected research_papers.json "
            "to contain a list of papers."
        )

    return data


# =========================================================
# Clean text
# =========================================================

def clean_text(
    value: Any
) -> str:

    if value is None:
        return ""

    text = str(value)

    return " ".join(
        text.split()
    ).strip()


# =========================================================
# Normalize paper
# =========================================================

def normalize_paper(
    paper: dict[str, Any]
) -> dict[str, Any]:

    enriched = dict(paper)

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    enriched["title"] = clean_text(
        paper.get("title")
    )

    # -----------------------------------------------------
    # Authors
    # -----------------------------------------------------

    authors = paper.get(
        "authors",
        []
    )

    if not isinstance(
        authors,
        list
    ):

        authors = []

    enriched["authors"] = [
        clean_text(author)
        for author in authors
        if clean_text(author)
    ]

    # -----------------------------------------------------
    # Abstract
    # -----------------------------------------------------

    abstract = clean_text(
        paper.get("summary")
    )

    enriched["abstract"] = abstract

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------

    enriched["paper_url"] = clean_text(
        paper.get("paper_url")
    )

    # -----------------------------------------------------
    # GitHub
    # -----------------------------------------------------

    github_url = paper.get(
        "github_url"
    )

    enriched["github_url"] = (
        clean_text(github_url)
        if github_url
        else None
    )

    github_stars = paper.get(
        "github_stars"
    )

    enriched["github_stars"] = (
        github_stars
        if isinstance(
            github_stars,
            int
        )
        else None
    )

    # -----------------------------------------------------
    # New fields for Day 2
    # -----------------------------------------------------

    enriched.setdefault(
        "keywords",
        []
    )

    enriched.setdefault(
        "topics",
        []
    )

    enriched.setdefault(
        "research_problem",
        None
    )

    enriched.setdefault(
        "proposed_method",
        None
    )

    enriched.setdefault(
        "datasets",
        []
    )

    enriched.setdefault(
        "evaluation_metrics",
        []
    )

    enriched.setdefault(
        "key_findings",
        None
    )

    enriched.setdefault(
        "limitations",
        None
    )

    return enriched


# =========================================================
# Fetch arXiv paper page
# =========================================================

async def fetch_paper_page(
    session: aiohttp.ClientSession,
    paper_url: str,
    semaphore: asyncio.Semaphore,
):

    if not paper_url:

        return None

    async with semaphore:

        try:

            async with session.get(
                paper_url
            ) as response:

                if response.status != 200:

                    return None

                return await response.text()

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ):

            return None


# =========================================================
# Enrich one paper
# =========================================================

async def enrich_one_paper(
    session: aiohttp.ClientSession,
    paper: dict[str, Any],
    semaphore: asyncio.Semaphore,
):

    enriched = normalize_paper(
        paper
    )

    # -----------------------------------------------------
    # Fetch arXiv page
    # -----------------------------------------------------

    html = await fetch_paper_page(
        session,
        enriched["paper_url"],
        semaphore,
    )

    # -----------------------------------------------------
    # Store basic page status
    # -----------------------------------------------------

    enriched["arxiv_page_available"] = (
        html is not None
    )

    return enriched


# =========================================================
# Enrich all papers
# =========================================================

async def enrich_papers(
    papers: list[dict[str, Any]]
):

    ssl_context = (
        create_ssl_context()
    )

    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=MAX_CONCURRENT_REQUESTS,
    )

    timeout = aiohttp.ClientTimeout(
        total=ARXIV_PAGE_TIMEOUT
    )

    headers = {
        "User-Agent": USER_AGENT
    }

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_REQUESTS
    )

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=headers,
    ) as session:

        tasks = [
            enrich_one_paper(
                session,
                paper,
                semaphore,
            )
            for paper in papers
        ]

        results = []

        for index, task in enumerate(
            asyncio.as_completed(tasks),
            start=1
        ):

            result = await task

            results.append(
                result
            )

            if index % 100 == 0:

                print(
                    f"[ENRICHED] "
                    f"{index} papers"
                )

    return results


# =========================================================
# Save enriched dataset
# =========================================================

def save_papers(
    papers: list[dict[str, Any]]
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            papers,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )


# =========================================================
# Main
# =========================================================

async def main():

    print("=" * 70)
    print("AI Intelligence Pipeline")
    print("Day 2 - Paper Enrichment")
    print("=" * 70)

    print(
        f"\nInput : {INPUT_FILE}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        "\nLoading Day 1 dataset..."
    )

    papers = load_papers()

    print(
        f"Loaded {len(papers)} papers."
    )

    print(
        "\nEnriching arXiv metadata..."
    )

    enriched_papers = (
        await enrich_papers(
            papers
        )
    )

    print(
        "\nSaving enriched dataset..."
    )

    save_papers(
        enriched_papers
    )

    print("\n" + "=" * 70)

    print(
        "DAY 2 - STEP 1 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Input papers  : {len(papers)}"
    )

    print(
        f"Output papers : "
        f"{len(enriched_papers)}"
    )

    print(
        f"Output file   : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )