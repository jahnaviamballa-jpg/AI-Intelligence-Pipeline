import json
from pathlib import Path


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/recommended_research_papers.json"
)


# =========================================================
# Helper
# =========================================================

def is_valid_url(url):
    if not url:
        return False

    return (
        isinstance(url, str)
        and (
            url.startswith("http://")
            or url.startswith("https://")
        )
    )


# =========================================================
# Main validation
# =========================================================

def main():

    print("=" * 70)

    print(
        "AI Intelligence Pipeline"
    )

    print(
        "Day 2 - Final Recommendation Dataset Validator"
    )

    print("=" * 70)

    # -----------------------------------------------------
    # Check file
    # -----------------------------------------------------

    print(
        f"\nDataset: {INPUT_FILE}"
    )

    if not INPUT_FILE.exists():

        print(
            "[FAIL] Dataset file does not exist."
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    try:

        with INPUT_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            papers = json.load(file)

    except json.JSONDecodeError as error:

        print(
            f"[FAIL] Invalid JSON: {error}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Basic dataset validation
    # -----------------------------------------------------

    print(
        f"Total records: {len(papers)}"
    )

    if len(papers) >= 1000:

        print(
            "[PASS] At least 1000 papers found."
        )

    else:

        print(
            "[FAIL] Fewer than 1000 papers found."
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Required fields
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

    missing_field_count = 0

    for field in required_fields:

        missing = sum(
            1
            for paper in papers
            if field not in paper
        )

        if missing == 0:

            print(
                f"[PASS] Field present: {field}"
            )

        else:

            print(
                f"[FAIL] {field} "
                f"missing in {missing} papers"
            )

            missing_field_count += 1

    if missing_field_count > 0:

        raise SystemExit(1)

    # -----------------------------------------------------
    # Duplicate paper URLs
    # -----------------------------------------------------

    urls = [
        paper.get("paper_url")
        for paper in papers
    ]

    unique_urls = set(urls)

    duplicate_count = (
        len(urls)
        - len(unique_urls)
    )

    if duplicate_count == 0:

        print(
            "[PASS] No duplicate paper URLs."
        )

    else:

        print(
            f"[FAIL] Duplicate URLs: "
            f"{duplicate_count}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Paper URL validation
    # -----------------------------------------------------

    invalid_paper_urls = sum(
        1
        for paper in papers
        if not is_valid_url(
            paper.get("paper_url")
        )
    )

    if invalid_paper_urls == 0:

        print(
            "[PASS] All paper URLs are valid."
        )

    else:

        print(
            f"[FAIL] Invalid paper URLs: "
            f"{invalid_paper_urls}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Recommendation score validation
    # -----------------------------------------------------

    invalid_scores = 0

    for paper in papers:

        score = paper.get(
            "recommendation_score"
        )

        if not isinstance(
            score,
            (int, float)
        ):

            invalid_scores += 1

            continue

        if score < 0 or score > 100:

            invalid_scores += 1

    if invalid_scores == 0:

        print(
            "[PASS] All recommendation scores "
            "are between 0 and 100."
        )

    else:

        print(
            f"[FAIL] Invalid recommendation "
            f"scores: {invalid_scores}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Recommendation categories
    # -----------------------------------------------------

    valid_categories = {
        "Highly Recommended",
        "Recommended",
        "Worth Exploring",
        "General",
    }

    invalid_categories = sum(
        1
        for paper in papers
        if paper.get(
            "recommendation_category"
        ) not in valid_categories
    )

    if invalid_categories == 0:

        print(
            "[PASS] All recommendation categories "
            "are valid."
        )

    else:

        print(
            f"[FAIL] Invalid recommendation "
            f"categories: {invalid_categories}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Recommendation rank validation
    # -----------------------------------------------------

    ranks = [
        paper.get(
            "recommendation_rank"
        )
        for paper in papers
    ]

    expected_ranks = list(
        range(
            1,
            len(papers) + 1
        )
    )

    if sorted(ranks) == expected_ranks:

        print(
            "[PASS] Recommendation rankings "
            "are complete and unique."
        )

    else:

        print(
            "[FAIL] Recommendation rankings "
            "are invalid."
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Check ranking order
    # -----------------------------------------------------

    ranking_correct = True

    for index in range(
        len(papers) - 1
    ):

        current_score = papers[index].get(
            "recommendation_score",
            0
        )

        next_score = papers[index + 1].get(
            "recommendation_score",
            0
        )

        if current_score < next_score:

            ranking_correct = False

            break

    if ranking_correct:

        print(
            "[PASS] Papers are sorted by "
            "recommendation score."
        )

    else:

        print(
            "[FAIL] Recommendation ranking "
            "order is incorrect."
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Recommendation reasons
    # -----------------------------------------------------

    invalid_reasons = 0

    for paper in papers:

        reasons = paper.get(
            "recommendation_reasons"
        )

        if not isinstance(
            reasons,
            list
        ):

            invalid_reasons += 1

    if invalid_reasons == 0:

        print(
            "[PASS] Recommendation reasons "
            "are valid."
        )

    else:

        print(
            f"[FAIL] Invalid recommendation "
            f"reasons: {invalid_reasons}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Trend fields
    # -----------------------------------------------------

    invalid_trends = 0

    for paper in papers:

        if not isinstance(
            paper.get("detected_trends"),
            list
        ):

            invalid_trends += 1

        if not isinstance(
            paper.get("trend_scores"),
            dict
        ):

            invalid_trends += 1

    if invalid_trends == 0:

        print(
            "[PASS] Trend enrichment fields "
            "are valid."
        )

    else:

        print(
            f"[FAIL] Invalid trend fields: "
            f"{invalid_trends}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # Calculate statistics
    # -----------------------------------------------------
    average_intelligence = (
    sum(
        float(
            paper.get(
                "research_intelligence_score",
                0
            )
        )
        for paper in papers
    )
    / len(papers)
)
    github_count = sum(
        1
        for paper in papers
        if paper.get("github_url")
    )

    highly_recommended = sum(
        1
        for paper in papers
        if paper.get(
            "recommendation_category"
        ) == "Highly Recommended"
    )

    recommended = sum(
        1
        for paper in papers
        if paper.get(
            "recommendation_category"
        ) == "Recommended"
    )

    worth_exploring = sum(
        1
        for paper in papers
        if paper.get(
            "recommendation_category"
        ) == "Worth Exploring"
    )

    general = sum(
        1
        for paper in papers
        if paper.get(
            "recommendation_category"
        ) == "General"
    )

    average_score = (
        sum(
            paper.get(
                "recommendation_score",
                0
            )
            for paper in papers
        )
        / len(papers)
    )

    # -----------------------------------------------------
    # Final summary
    # -----------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "DAY 2 FINAL DATASET VALIDATION"
    )

    print(
        "=" * 70
    )

    print(
        f"Total papers          : {len(papers)}"
    )

    print(
        f"GitHub repositories   : {github_count}"
    )

    print(
        f"Highly Recommended    : "
        f"{highly_recommended}"
    )

    print(
        f"Recommended           : "
        f"{recommended}"
    )

    print(
        f"Worth Exploring      : "
        f"{worth_exploring}"
    )

    print(
        f"General               : "
        f"{general}"
    )

    print(
        f"Average recommendation "
        f"score                : "
        f"{average_score:.2f}"
    )
    print(
    f"Average intelligence "
    f"score                : "
    f"{average_intelligence:.2f}"
)
    print(
        "=" * 70
    )

    print(
        "DAY 2 DATASET VALIDATION PASSED"
    )

    print(
        "Day 2 enrichment pipeline is ready."
    )

    print(
        "=" * 70
    )


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()