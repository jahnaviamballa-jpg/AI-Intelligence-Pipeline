import asyncio
import json
import ssl
from pathlib import Path
from datetime import datetime, timezone

import aiohttp
import certifi
import feedparser

from src.enrichers.github_enricher import enrich_papers
from src.models.research_paper import ResearchPaper


# =========================================================
# Configuration
# =========================================================

ARXIV_API_URL = "https://export.arxiv.org/api/query"

TARGET_PAPERS = 1000

BATCH_SIZE = 100

MAX_RETRIES = 3

REQUEST_TIMEOUT = 30

OUTPUT_FILE = Path(
    "data/processed/research_papers.json"
)

CHECKPOINT_FILE = Path(
    "data/processed/arxiv_checkpoint.json"
)

USER_AGENT = (
    "AI-Intelligence-Pipeline/1.0 "
    "(research-data-ingestion)"
)

SEARCH_QUERY = (
    "cat:cs.AI OR "
    "cat:cs.LG OR "
    "cat:cs.CL"
)


# =========================================================
# SSL
# =========================================================

def create_ssl_context():

    return ssl.create_default_context(
        cafile=certifi.where()
    )


# =========================================================
# Fetch one arXiv batch
# =========================================================

async def fetch_arxiv_batch(
    session: aiohttp.ClientSession,
    start: int,
    batch_size: int,
):

    params = {
        "search_query": SEARCH_QUERY,
        "start": start,
        "max_results": batch_size,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            async with session.get(
                ARXIV_API_URL,
                params=params,
            ) as response:

                # -----------------------------------------
                # Rate limit
                # -----------------------------------------

                if response.status == 429:

                    retry_after = (
                        response.headers.get(
                            "Retry-After"
                        )
                    )

                    delay = (
                        float(retry_after)
                        if retry_after
                        else 2 ** attempt
                    )

                    print(
                        f"[429] Batch starting "
                        f"at {start}. "
                        f"Retrying in {delay}s"
                    )

                    await asyncio.sleep(
                        delay
                    )

                    continue

                # -----------------------------------------
                # Server errors
                # -----------------------------------------

                if response.status >= 500:

                    delay = 2 ** attempt

                    print(
                        f"[{response.status}] "
                        f"Batch {start}. "
                        f"Retrying in {delay}s"
                    )

                    await asyncio.sleep(
                        delay
                    )

                    continue

                response.raise_for_status()

                xml_data = await response.text()

                return parse_arxiv_response(
                    xml_data
                )

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ) as error:

            if attempt == MAX_RETRIES:

                print(
                    f"[FAILED] Batch "
                    f"{start}: {error}"
                )

                return []

            delay = 2 ** attempt

            print(
                f"[RETRY {attempt}] "
                f"Batch {start}. "
                f"Waiting {delay}s"
            )

            await asyncio.sleep(
                delay
            )

    return []


# =========================================================
# Parse arXiv response
# =========================================================

def parse_arxiv_response(
    xml_data: str
):

    feed = feedparser.parse(
        xml_data
    )

    papers = []

    for entry in feed.entries:

        # ---------------------------------------------
        # arXiv ID
        # ---------------------------------------------

        paper_url = entry.get(
            "id"
        )

        arxiv_id = None

        if paper_url:

            arxiv_id = (
                paper_url
                .rstrip("/")
                .split("/")
                [-1]
            )

        # ---------------------------------------------
        # Authors
        # ---------------------------------------------

        authors = [
            author.name
            for author in entry.get(
                "authors",
                []
            )
        ]

        # ---------------------------------------------
        # Published date
        # ---------------------------------------------

        published = entry.get(
            "published_parsed"
        )

        if published:

            published_date = datetime(
                *published[:6],
                tzinfo=timezone.utc,
            )

        else:

            published_date = None

        # ---------------------------------------------
        # Summary
        # ---------------------------------------------

        summary = (
            entry.get(
                "summary",
                ""
            )
            .strip()
            .replace(
                "\n",
                " "
            )
        )

        # ---------------------------------------------
        # Links
        # ---------------------------------------------

        links = entry.get(
            "links",
            []
        )

        links_text = " ".join(
            link.get(
                "href",
                ""
            )
            for link in links
        )

        # ---------------------------------------------
        # Paper record
        # ---------------------------------------------

        paper = {

            "arxiv_id": arxiv_id,

            "title": (
                entry.get(
                    "title",
                    ""
                )
                .strip()
                .replace(
                    "\n",
                    " "
                )
            ),

            "authors": authors,

            "paper_url": paper_url,

            "published_date": (
                published_date
            ),

            "summary": summary,

            "links_text": links_text,

            "github_url": None,

            "github_stars": None,
        }

        papers.append(
            paper
        )

    return papers


# =========================================================
# Deduplicate papers
# =========================================================

def deduplicate_papers(
    papers
):

    unique = {}

    for paper in papers:

        arxiv_id = paper.get(
            "arxiv_id"
        )

        if not arxiv_id:
            continue

        if arxiv_id not in unique:

            unique[arxiv_id] = paper

    return list(
        unique.values()
    )


# =========================================================
# Save checkpoint
# =========================================================

def save_checkpoint(
    papers
):

    CHECKPOINT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    serializable = []

    for paper in papers:

        item = paper.copy()

        if isinstance(
            item.get("published_date"),
            datetime
        ):

            item[
                "published_date"
            ] = item[
                "published_date"
            ].isoformat()

        serializable.append(
            item
        )

    with open(
        CHECKPOINT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            serializable,
            file,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# Validate papers
# =========================================================

def validate_papers(
    papers
):

    validated = []

    print(
        "\nValidating papers...\n"
    )

    for index, paper in enumerate(
        papers,
        start=1
    ):

        try:

            validated_paper = ResearchPaper(
                title=paper[
                    "title"
                ],

                authors=paper[
                    "authors"
                ],

                paper_url=paper[
                    "paper_url"
                ],

                github_url=paper.get(
                    "github_url"
                ),

                github_stars=paper.get(
                    "github_stars"
                ),

                published_date=paper[
                    "published_date"
                ],
            )

            validated.append(
                validated_paper
            )

            if index % 100 == 0:

                print(
                    f"[VALID] "
                    f"{index} papers validated"
                )

        except Exception as error:

            print(
                f"[INVALID] "
                f"{paper.get('title')}"
            )

            print(
                f"Reason: {error}"
            )

    return validated


# =========================================================
# Save final JSON
# =========================================================

def save_final_json(papers):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = []

    for paper in papers:

        # Pydantic v2
        item = paper.model_dump(
            mode="json"
        )

        data.append(item)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"\nSaved {len(data)} papers "
        f"to {OUTPUT_FILE}"
    )


# =========================================================
# Main crawler
# =========================================================

async def main():

    print("=" * 70)

    print(
        "AI Intelligence Pipeline"
    )

    print(
        "Scalable arXiv Research Paper Crawler"
    )

    print("=" * 70)

    print()

    print(
        f"Target papers : {TARGET_PAPERS}"
    )

    print(
        f"Batch size    : {BATCH_SIZE}"
    )

    print(
        f"Search query  : {SEARCH_QUERY}"
    )

    print()

    # -----------------------------------------------------
    # SSL
    # -----------------------------------------------------

    ssl_context = (
        create_ssl_context()
    )

    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=10,
    )

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    headers = {
        "User-Agent": USER_AGENT
    }

    all_papers = []

    # -----------------------------------------------------
    # Create session
    # -----------------------------------------------------

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=headers,
    ) as session:

        start = 0

        batch_number = 0

        while len(all_papers) < TARGET_PAPERS:

            batch_number += 1

            print(
                "-" * 70
            )

            print(
                f"Fetching batch "
                f"{batch_number}"
            )

            print(
                f"Start index: {start}"
            )

            batch = await fetch_arxiv_batch(
                session,
                start,
                BATCH_SIZE,
            )

            if not batch:

                print(
                    "No more papers returned."
                )

                break

            all_papers.extend(
                batch
            )

            # ---------------------------------------------
            # Deduplicate
            # ---------------------------------------------

            all_papers = (
                deduplicate_papers(
                    all_papers
                )
            )

            print(
                f"Batch fetched: "
                f"{len(batch)}"
            )

            print(
                f"Unique papers: "
                f"{len(all_papers)}"
            )

            # ---------------------------------------------
            # Checkpoint
            # ---------------------------------------------

            save_checkpoint(
                all_papers
            )

            print(
                "Checkpoint saved."
            )

            # ---------------------------------------------
            # Stop when target reached
            # ---------------------------------------------

            if len(all_papers) >= TARGET_PAPERS:

                all_papers = (
                    all_papers[
                        :TARGET_PAPERS
                    ]
                )

                break

            start += BATCH_SIZE

            # ---------------------------------------------
            # Respect arXiv
            # ---------------------------------------------

            await asyncio.sleep(
                3
            )

    # -----------------------------------------------------
    # Summary after collection
    # -----------------------------------------------------

    print()
    print("=" * 70)

    print(
        "Bulk collection completed"
    )

    print(
        f"Unique papers collected: "
        f"{len(all_papers)}"
    )

    print("=" * 70)

    # -----------------------------------------------------
    # GitHub enrichment
    # -----------------------------------------------------

    print(
        "\nEnriching papers with "
        "GitHub data..."
    )

    all_papers = await enrich_papers(
        all_papers
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    validated_papers = (
        validate_papers(
            all_papers
        )
    )

    # -----------------------------------------------------
    # Save final result
    # -----------------------------------------------------

    save_final_json(
        validated_papers
    )

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    github_count = sum(
        1
        for paper in validated_papers
        if paper.github_url
    )

    print()

    print("=" * 70)

    print(
        "FINAL PIPELINE SUMMARY"
    )

    print("=" * 70)

    print(
        f"Fetched       : "
        f"{len(all_papers)}"
    )

    print(
        f"Validated     : "
        f"{len(validated_papers)}"
    )

    print(
        f"GitHub repos  : "
        f"{github_count}"
    )

    print(
        f"Output        : "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Checkpoint    : "
        f"{CHECKPOINT_FILE}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )