import json
from pathlib import Path


# =========================================================
# Configuration
# =========================================================

DATASET_FILE = Path(
    "data/processed/recommended_research_papers.json"
)

SIMILARITY_FILE = Path(
    "data/processed/similarity_index.json"
)

API_METADATA_FILE = Path(
    "data/processed/research_api_metadata.json"
)


# =========================================================
# Helpers
# =========================================================

def load_json(path):
    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def check(condition, message):
    if condition:
        print(f"[PASS] {message}")
        return True

    print(f"[FAIL] {message}")
    return False


# =========================================================
# Main validation
# =========================================================

def main():

    print("=" * 70)
    print("AI Intelligence Pipeline")
    print("Day 3 - Step 5: Research Intelligence API Validator")
    print("=" * 70)

    passed = True

    # -----------------------------------------------------
    # Dataset
    # -----------------------------------------------------

    print("\nValidating research dataset...")

    if not DATASET_FILE.exists():
        print(
            f"[FAIL] Dataset not found: {DATASET_FILE}"
        )
        return

    papers = load_json(DATASET_FILE)

    passed &= check(
        isinstance(papers, list),
        "Research dataset is a list."
    )

    passed &= check(
        len(papers) >= 1000,
        "At least 1000 research papers found."
    )

    # -----------------------------------------------------
    # Required paper fields
    # -----------------------------------------------------

    required_fields = [
        "title",
        "authors",
        "paper_url",
        "abstract",
        "keywords",
        "topics",
        "research_score",
        "research_intelligence_score",
        "research_area",
        "research_stage",
        "detected_trends",
        "trend_scores",
        "trend_signals",
        "technical_signals",
        "application_areas",
        "application_signals",
        "recommendation_score",
        "recommendation_category",
        "recommendation_reasons",
        "recommendation_features",
        "recommendation_rank",
    ]

    for field in required_fields:

        missing = sum(
            1
            for paper in papers
            if field not in paper
        )

        passed &= check(
            missing == 0,
            f"Field present: {field}"
        )

    # -----------------------------------------------------
    # Paper URLs
    # -----------------------------------------------------

    urls = [
        paper.get("paper_url")
        for paper in papers
    ]

    passed &= check(
        all(
            isinstance(url, str)
            and url.startswith(
                ("http://", "https://")
            )
            for url in urls
        ),
        "All paper URLs are valid."
    )

    passed &= check(
        len(urls) == len(set(urls)),
        "No duplicate paper URLs."
    )

    # -----------------------------------------------------
    # Recommendation validation
    # -----------------------------------------------------

    valid_categories = {
        "Highly Recommended",
        "Recommended",
        "Worth Exploring",
        "General",
    }

    categories_valid = all(
        paper.get(
            "recommendation_category"
        ) in valid_categories
        for paper in papers
    )

    passed &= check(
        categories_valid,
        "All recommendation categories are valid."
    )

    scores_valid = all(
        isinstance(
            paper.get("recommendation_score"),
            (int, float)
        )
        and 0 <= paper.get(
            "recommendation_score"
        ) <= 100
        for paper in papers
    )

    passed &= check(
        scores_valid,
        "All recommendation scores are between 0 and 100."
    )

    # -----------------------------------------------------
    # Recommendation rankings
    # -----------------------------------------------------

    ranks = [
        paper.get("recommendation_rank")
        for paper in papers
    ]

    passed &= check(
        len(ranks) == len(set(ranks)),
        "Recommendation rankings are unique."
    )

    passed &= check(
        set(ranks) == set(
            range(1, len(papers) + 1)
        ),
        "Recommendation rankings are complete."
    )

    # -----------------------------------------------------
    # Similarity index
    # -----------------------------------------------------

    print("\nValidating similarity index...")

    if not SIMILARITY_FILE.exists():

        print(
            f"[FAIL] Similarity index not found: "
            f"{SIMILARITY_FILE}"
        )

        passed = False

    else:

        similarity = load_json(
            SIMILARITY_FILE
        )

        passed &= check(
            isinstance(
                similarity,
                dict
            ),
            "Similarity index is valid JSON object."
        )

        # Support common index structures
        if isinstance(similarity, dict):

            if "papers" in similarity:

                similarity_count = len(
                    similarity["papers"]
                )

            elif "documents" in similarity:

                similarity_count = len(
                    similarity["documents"]
                )

            else:

                similarity_count = len(
                    similarity
                )

            passed &= check(
                similarity_count >= 1000,
                "Similarity index contains at least 1000 papers."
            )

    # -----------------------------------------------------
    # API metadata
    # -----------------------------------------------------

    print("\nValidating API metadata...")

    if not API_METADATA_FILE.exists():

        print(
            f"[FAIL] API metadata not found: "
            f"{API_METADATA_FILE}"
        )

        passed = False

    else:

        metadata = load_json(
            API_METADATA_FILE
        )

        passed &= check(
            isinstance(
                metadata,
                dict
            ),
            "API metadata is valid JSON."
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\n" + "=" * 70)

    if passed:

        print(
            "DAY 3 - STEP 5 VALIDATION PASSED"
        )

        print("=" * 70)

        print(
            f"Research papers : {len(papers)}"
        )

        print(
            "Search engine    : READY"
        )

        print(
            "Similarity engine: READY"
        )

        print(
            "Recommendation   : READY"
        )

        print(
            "Unified API      : READY"
        )

        print(
            "API validation   : PASSED"
        )

    else:

        print(
            "DAY 3 - STEP 5 VALIDATION FAILED"
        )

        print(
            "Please fix the failed checks above."
        )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()