import json
from pathlib import Path
from collections import Counter


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/trend_enriched_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/recommended_research_papers.json"
)

PROGRESS_INTERVAL = 100


# =========================================================
# Weights
# =========================================================

WEIGHTS = {
    "research_score": 0.30,
    "intelligence_score": 0.25,
    "github_stars": 0.10,
    "trend_score": 0.15,
    "keyword_score": 0.10,
    "emerging_bonus": 0.10,
}


# =========================================================
# Load dataset
# =========================================================

def load_dataset():

    print(
        "\nLoading trend-enriched dataset..."
    )

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found: "
            f"{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    print(
        f"Loaded {len(papers)} papers."
    )

    return papers


# =========================================================
# Safe numeric conversion
# =========================================================

def safe_float(value):

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


# =========================================================
# Normalize score
# =========================================================

def normalize_score(
    value,
    maximum
):

    value = safe_float(value)

    if maximum <= 0:
        return 0.0

    score = (
        value / maximum
    ) * 100

    return min(
        100.0,
        score
    )


# =========================================================
# Calculate trend score
# =========================================================

def calculate_trend_score(
    paper
):

    trend_scores = paper.get(
        "trend_scores",
        {}
    )

    if not isinstance(
        trend_scores,
        dict
    ):

        return 0.0

    if not trend_scores:
        return 0.0

    total = sum(
        safe_float(value)
        for value in trend_scores.values()
    )

    # More detected trend signals
    # means broader research relevance.

    return min(
        100.0,
        total * 10
    )


# =========================================================
# Calculate keyword score
# =========================================================

def calculate_keyword_score(
    paper
):

    keywords = paper.get(
        "keywords",
        []
    )

    if not isinstance(
        keywords,
        list
    ):

        return 0.0

    count = len(
        keywords
    )

    return min(
        100.0,
        count * 10
    )


# =========================================================
# Calculate GitHub score
# =========================================================

def calculate_github_score(
    paper,
    max_stars
):

    stars = safe_float(
        paper.get(
            "github_stars",
            0
        )
    )

    if stars <= 0:
        return 0.0

    # Log-like normalization.
    # Prevents extremely popular repositories
    # from dominating the recommendation score.

    if max_stars <= 0:
        return 0.0

    import math

    score = (
        math.log1p(stars)
        /
        math.log1p(max_stars)
    ) * 100

    return min(
        100.0,
        score
    )


# =========================================================
# Emerging research bonus
# =========================================================

def calculate_emerging_bonus(
    paper
):

    stage = str(
        paper.get(
            "research_stage",
            ""
        )
    ).strip().lower()

    if stage == "emerging":
        return 100.0

    if stage == "developing":
        return 50.0

    if stage == "mature":
        return 20.0

    return 0.0


# =========================================================
# Generate recommendation reasons
# =========================================================

def generate_reasons(
    paper,
    research_score,
    intelligence_score,
    trend_score,
    github_score,
    emerging_bonus
):

    reasons = []

    trends = paper.get(
        "detected_trends",
        []
    )

    if trends:

        reasons.append(
            "Relevant to: "
            + ", ".join(
                trends[:3]
            )
        )

    if research_score >= 70:

        reasons.append(
            "High research quality score"
        )

    elif research_score >= 50:

        reasons.append(
            "Good research quality score"
        )

    if intelligence_score >= 70:

        reasons.append(
            "Strong research intelligence"
        )

    elif intelligence_score >= 50:

        reasons.append(
            "Good research intelligence"
        )

    if trend_score >= 50:

        reasons.append(
            "Strong trend relevance"
        )

    if github_score >= 50:

        reasons.append(
            "Has a well-supported GitHub repository"
        )

    if emerging_bonus >= 80:

        reasons.append(
            "Emerging research area"
        )

    applications = paper.get(
        "application_areas",
        []
    )

    if applications:

        reasons.append(
            "Potential application: "
            + applications[0]
        )

    return reasons[:5]


# =========================================================
# Calculate recommendation score
# =========================================================

def calculate_recommendation_score(
    paper,
    max_stars
):

    research_score = normalize_score(
        paper.get(
            "research_score",
            0
        ),
        100
    )

    intelligence_score = normalize_score(
        paper.get(
            "intelligence_score",
            0
        ),
        100
    )

    github_score = calculate_github_score(
        paper,
        max_stars
    )

    trend_score = calculate_trend_score(
        paper
    )

    keyword_score = calculate_keyword_score(
        paper
    )

    emerging_bonus = calculate_emerging_bonus(
        paper
    )

    final_score = (

        research_score
        * WEIGHTS["research_score"]

        +

        intelligence_score
        * WEIGHTS["intelligence_score"]

        +

        github_score
        * WEIGHTS["github_stars"]

        +

        trend_score
        * WEIGHTS["trend_score"]

        +

        keyword_score
        * WEIGHTS["keyword_score"]

        +

        emerging_bonus
        * WEIGHTS["emerging_bonus"]
    )

    reasons = generate_reasons(
        paper,
        research_score,
        intelligence_score,
        trend_score,
        github_score,
        emerging_bonus
    )

    paper["recommendation_score"] = round(
        final_score,
        2
    )

    paper["recommendation_reasons"] = (
        reasons
    )

    paper["recommendation_features"] = {

        "research_quality": round(
            research_score,
            2
        ),

        "research_intelligence": round(
            intelligence_score,
            2
        ),

        "github_score": round(
            github_score,
            2
        ),

        "trend_relevance": round(
            trend_score,
            2
        ),

        "keyword_strength": round(
            keyword_score,
            2
        ),

        "emerging_bonus": round(
            emerging_bonus,
            2
        ),
    }

    return paper


# =========================================================
# Assign recommendation category
# =========================================================

def assign_category(
    score
):

    if score >= 80:
        return "Highly Recommended"

    if score >= 65:
        return "Recommended"

    if score >= 50:
        return "Worth Exploring"

    return "General"


# =========================================================
# Recommend papers
# =========================================================

def recommend_papers(
    papers
):

    print(
        "\nCalculating research recommendations..."
    )

    max_stars = 0

    for paper in papers:

        stars = safe_float(
            paper.get(
                "github_stars",
                0
            )
        )

        max_stars = max(
            max_stars,
            stars
        )

    enriched = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        paper = calculate_recommendation_score(
            paper,
            max_stars
        )

        paper["recommendation_category"] = (
            assign_category(
                paper[
                    "recommendation_score"
                ]
            )
        )

        enriched.append(
            paper
        )

        if (
            index % PROGRESS_INTERVAL
            == 0
        ):

            print(
                f"[RECOMMENDED] "
                f"{index} papers processed"
            )

    # Highest recommendation first.

    enriched.sort(
        key=lambda paper:
        paper.get(
            "recommendation_score",
            0
        ),
        reverse=True
    )

    # Assign ranking.

    for rank, paper in enumerate(
        enriched,
        start=1
    ):

        paper["recommendation_rank"] = (
            rank
        )

    return enriched


# =========================================================
# Calculate statistics
# =========================================================

def calculate_statistics(
    papers
):

    category_counter = Counter()

    trend_counter = Counter()

    total_score = 0.0

    for paper in papers:

        category = paper.get(
            "recommendation_category"
        )

        if category:

            category_counter[
                category
            ] += 1

        total_score += safe_float(
            paper.get(
                "recommendation_score",
                0
            )
        )

        for trend in paper.get(
            "detected_trends",
            []
        ):

            trend_counter[
                trend
            ] += 1

    average_score = (
        total_score / len(papers)
        if papers
        else 0
    )

    return (
        category_counter,
        trend_counter,
        average_score,
    )


# =========================================================
# Save dataset
# =========================================================

def save_dataset(
    papers
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\nSaving recommended dataset..."
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            papers,
            file,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 70)

    print(
        "AI Intelligence Pipeline"
    )

    print(
        "Day 2 - Step 7: Research Recommendation Engine"
    )

    print("=" * 70)

    papers = load_dataset()

    recommended_papers = recommend_papers(
        papers
    )

    (
        category_counter,
        trend_counter,
        average_score,
    ) = calculate_statistics(
        recommended_papers
    )

    # -----------------------------------------------------
    # Recommendation distribution
    # -----------------------------------------------------

    print(
        "\nRecommendation distribution:"
    )

    for category in [
        "Highly Recommended",
        "Recommended",
        "Worth Exploring",
        "General",
    ]:

        print(
            f"{category:<22} "
            f"{category_counter.get(category, 0)}"
        )

    # -----------------------------------------------------
    # Average score
    # -----------------------------------------------------

    print(
        f"\nAverage recommendation score: "
        f"{average_score:.2f}"
    )

    # -----------------------------------------------------
    # Top papers
    # -----------------------------------------------------

    print(
        "\nTop 10 recommended papers:"
    )

    for paper in recommended_papers[:10]:

        title = str(
            paper.get(
                "title",
                "Unknown"
            )
        ).replace(
            "\n",
            " "
        )

        score = paper.get(
            "recommendation_score",
            0
        )

        category = paper.get(
            "recommendation_category",
            "General"
        )

        print(
            f"{paper['recommendation_rank']:2}. "
            f"{title[:65]:<65} "
            f"{score:6.2f} "
            f"{category}"
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_dataset(
        recommended_papers
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "DAY 2 - STEP 7 COMPLETED"
    )

    print(
        "=" * 70
    )

    print(
        f"Total papers : "
        f"{len(recommended_papers)}"
    )

    print(
        f"Average score: "
        f"{average_score:.2f}"
    )

    print(
        "Output       : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()