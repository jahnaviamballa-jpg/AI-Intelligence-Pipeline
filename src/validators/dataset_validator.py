import json
from pathlib import Path
from urllib.parse import urlparse


# =========================================================
# Configuration
# =========================================================

DATA_FILE = Path(
    "data/processed/research_papers.json"
)

EXPECTED_MINIMUM = 1000


# =========================================================
# Load dataset
# =========================================================

def load_papers():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    with DATA_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# URL validation
# =========================================================

def is_valid_url(url):

    if not isinstance(url, str):
        return False

    try:

        parsed = urlparse(url)

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )

    except Exception:

        return False


# =========================================================
# Main validation
# =========================================================

def validate_dataset():

    print("=" * 70)
    print("AI Intelligence Pipeline")
    print("Research Dataset Validator")
    print("=" * 70)

    print(
        f"\nDataset: {DATA_FILE}"
    )

    papers = load_papers()

    print(
        f"Total records: {len(papers)}"
    )

    # -----------------------------------------------------
    # Record count
    # -----------------------------------------------------

    if len(papers) >= EXPECTED_MINIMUM:

        print(
            f"[PASS] At least "
            f"{EXPECTED_MINIMUM} papers found."
        )

    else:

        print(
            f"[FAIL] Expected at least "
            f"{EXPECTED_MINIMUM} papers."
        )

    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

    required_fields = [
        "title",
        "authors",
        "paper_url",
        "published_date",
    ]

    field_errors = 0

    for index, paper in enumerate(
        papers,
        start=1
    ):

        for field in required_fields:

            if field not in paper:

                print(
                    f"[FAIL] Paper #{index} "
                    f"missing field: {field}"
                )

                field_errors += 1

    if field_errors == 0:

        print(
            "[PASS] Required fields present "
            "in all papers."
        )

    # -----------------------------------------------------
    # Duplicate papers
    # -----------------------------------------------------

    urls = [
        paper.get("paper_url")
        for paper in papers
    ]

    unique_urls = set(urls)

    duplicates = (
        len(urls) - len(unique_urls)
    )

    if duplicates == 0:

        print(
            "[PASS] No duplicate paper URLs."
        )

    else:

        print(
            f"[FAIL] {duplicates} "
            f"duplicate paper URLs found."
        )

    # -----------------------------------------------------
    # Empty titles
    # -----------------------------------------------------

    empty_titles = sum(
        1
        for paper in papers
        if not str(
            paper.get("title", "")
        ).strip()
    )

    if empty_titles == 0:

        print(
            "[PASS] All papers have titles."
        )

    else:

        print(
            f"[FAIL] {empty_titles} "
            f"papers have empty titles."
        )

    # -----------------------------------------------------
    # Authors
    # -----------------------------------------------------

    invalid_authors = 0

    for paper in papers:

        authors = paper.get(
            "authors"
        )

        if not isinstance(
            authors,
            list
        ) or not authors:

            invalid_authors += 1

    if invalid_authors == 0:

        print(
            "[PASS] All papers have authors."
        )

    else:

        print(
            f"[FAIL] {invalid_authors} "
            f"papers have invalid authors."
        )

    # -----------------------------------------------------
    # arXiv URLs
    # -----------------------------------------------------

    invalid_arxiv_urls = 0

    for paper in papers:

        url = paper.get(
            "paper_url"
        )

        if not is_valid_url(url):

            invalid_arxiv_urls += 1

    if invalid_arxiv_urls == 0:

        print(
            "[PASS] All paper URLs are valid."
        )

    else:

        print(
            f"[FAIL] {invalid_arxiv_urls} "
            f"invalid paper URLs."
        )

    # -----------------------------------------------------
    # GitHub statistics
    # -----------------------------------------------------

    github_repositories = [
        paper
        for paper in papers
        if paper.get("github_url")
    ]

    print(
        f"\nGitHub repositories: "
        f"{len(github_repositories)}"
    )

    github_without_stars = sum(
        1
        for paper in github_repositories
        if paper.get("github_stars") is None
    )

    if github_without_stars == 0:

        print(
            "[PASS] All GitHub repositories "
            "have star counts."
        )

    else:

        print(
            f"[INFO] {github_without_stars} "
            f"GitHub repositories have no "
            f"star count."
        )

    # -----------------------------------------------------
    # GitHub URL validation
    # -----------------------------------------------------

    invalid_github_urls = 0

    for paper in github_repositories:

        if not is_valid_url(
            paper.get("github_url")
        ):

            invalid_github_urls += 1

    if invalid_github_urls == 0:

        print(
            "[PASS] GitHub URLs are valid."
        )

    else:

        print(
            f"[FAIL] {invalid_github_urls} "
            f"invalid GitHub URLs."
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("DATASET VALIDATION SUMMARY")
    print("=" * 70)

    print(
        f"Total papers       : {len(papers)}"
    )

    print(
        f"Unique papers      : {len(unique_urls)}"
    )

    print(
        f"GitHub repositories: "
        f"{len(github_repositories)}"
    )

    print(
        f"Duplicate URLs     : {duplicates}"
    )

    print(
        f"Invalid paper URLs : "
        f"{invalid_arxiv_urls}"
    )

    print(
        f"Invalid GitHub URLs: "
        f"{invalid_github_urls}"
    )

    print("=" * 70)

    if (
        len(papers) >= EXPECTED_MINIMUM
        and duplicates == 0
        and field_errors == 0
        and empty_titles == 0
        and invalid_authors == 0
        and invalid_arxiv_urls == 0
        and invalid_github_urls == 0
    ):

        print(
            "DATASET VALIDATION PASSED"
        )

        print(
            "Day 1 dataset collection is ready."
        )

    else:

        print(
            "DATASET VALIDATION NEEDS ATTENTION"
        )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    validate_dataset()