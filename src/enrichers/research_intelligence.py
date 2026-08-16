import json
from datetime import datetime, timezone
from pathlib import Path


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/scored_research_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/research_intelligence_papers.json"
)

PROGRESS_INTERVAL = 100


# =========================================================
# Load dataset
# =========================================================

def load_dataset():

    print("Loading scored research dataset...")

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
# Parse publication date
# =========================================================

def parse_date(value):

    if not value:
        return None

    if isinstance(value, datetime):

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value

    value = str(value)

    # ISO timestamp
    try:
        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )
    except ValueError:
        pass

    # Date only
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


# =========================================================
# Recency score
# =========================================================

def calculate_recency_score(paper):

    published_date = parse_date(
        paper.get(
            "published_date"
        )
    )

    if not published_date:
        return 0

    now = datetime.now(
        timezone.utc
    )

    age_days = (
        now - published_date
    ).days

    if age_days < 0:
        age_days = 0

    # Very recent research
    if age_days <= 30:
        return 20

    # Recent
    if age_days <= 90:
        return 18

    if age_days <= 180:
        return 15

    if age_days <= 365:
        return 12

    if age_days <= 730:
        return 8

    if age_days <= 1095:
        return 5

    return 2


# =========================================================
# GitHub impact score
# =========================================================

def calculate_impact_score(paper):

    stars = paper.get(
        "github_stars"
    )

    if stars is None:
        return 0

    try:
        stars = int(stars)
    except (
        ValueError,
        TypeError
    ):
        return 0

    if stars >= 5000:
        return 20

    if stars >= 2000:
        return 18

    if stars >= 1000:
        return 16

    if stars >= 500:
        return 14

    if stars >= 100:
        return 12

    if stars >= 50:
        return 10

    if stars >= 20:
        return 8

    if stars >= 10:
        return 6

    if stars > 0:
        return 4

    return 1


# =========================================================
# Abstract quality score
# =========================================================

def calculate_abstract_score(paper):

    summary = paper.get(
        "summary",
        ""
    )

    if not summary:
        return 0

    summary = str(
        summary
    ).strip()

    word_count = len(
        summary.split()
    )

    if word_count >= 250:
        return 20

    if word_count >= 180:
        return 17

    if word_count >= 120:
        return 14

    if word_count >= 80:
        return 10

    if word_count >= 40:
        return 6

    return 3


# =========================================================
# Author information score
# =========================================================

def calculate_author_score(paper):

    authors = paper.get(
        "authors",
        []
    )

    if not isinstance(
        authors,
        list
    ):
        return 0

    count = len(authors)

    if count >= 8:
        return 10

    if count >= 5:
        return 9

    if count >= 3:
        return 8

    if count == 2:
        return 7

    if count == 1:
        return 5

    return 0


# =========================================================
# Repository availability score
# =========================================================

def calculate_repository_score(paper):

    github_url = paper.get(
        "github_url"
    )

    if github_url:
        return 10

    return 0


# =========================================================
# Calculate intelligence score
# =========================================================

def calculate_intelligence_score(paper):

    recency_score = (
        calculate_recency_score(
            paper
        )
    )

    impact_score = (
        calculate_impact_score(
            paper
        )
    )

    abstract_score = (
        calculate_abstract_score(
            paper
        )
    )

    author_score = (
        calculate_author_score(
            paper
        )
    )

    repository_score = (
        calculate_repository_score(
            paper
        )
    )

    total = (
        recency_score
        + impact_score
        + abstract_score
        + author_score
        + repository_score
    )

    # Maximum:
    #
    # Recency      = 20
    # Impact       = 20
    # Abstract     = 20
    # Authors      = 10
    # Repository   = 10
    #
    # Maximum      = 80
    #
    # Normalize to 100.

    intelligence_score = round(
        (total / 80) * 100,
        2
    )

    return {
        "recency_score": recency_score,
        "impact_score": impact_score,
        "abstract_score": abstract_score,
        "author_score": author_score,
        "repository_score": repository_score,
        "research_intelligence_score":
            intelligence_score,
    }


# =========================================================
# Intelligence label
# =========================================================

def get_intelligence_label(score):

    if score >= 75:
        return "Very High"

    if score >= 60:
        return "High"

    if score >= 40:
        return "Medium"

    return "Low"


# =========================================================
# Enrich papers
# =========================================================

def enrich_papers(papers):

    print(
        "\nCalculating research intelligence..."
    )

    enriched = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        scores = (
            calculate_intelligence_score(
                paper
            )
        )

        paper.update(
            scores
        )

        paper[
            "intelligence_label"
        ] = get_intelligence_label(
            scores[
                "research_intelligence_score"
            ]
        )

        enriched.append(
            paper
        )

        if (
            index % PROGRESS_INTERVAL
            == 0
        ):

            print(
                f"[INTELLIGENCE] "
                f"{index} papers processed"
            )

    return enriched


# =========================================================
# Calculate statistics
# =========================================================

def calculate_statistics(papers):

    distribution = {
        "Very High": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
    }

    total_score = 0

    for paper in papers:

        label = paper.get(
            "intelligence_label",
            "Low"
        )

        distribution[
            label
        ] = distribution.get(
            label,
            0
        ) + 1

        total_score += paper.get(
            "research_intelligence_score",
            0
        )

    average = 0

    if papers:

        average = round(
            total_score / len(papers),
            2
        )

    return distribution, average


# =========================================================
# Save dataset
# =========================================================

def save_dataset(papers):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\nSaving research intelligence dataset..."
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
        "Day 2 - Step 5: Research Intelligence"
    )

    print("=" * 70)

    papers = load_dataset()

    enriched_papers = enrich_papers(
        papers
    )

    distribution, average = (
        calculate_statistics(
            enriched_papers
        )
    )

    print(
        "\nResearch intelligence distribution:"
    )

    print(
        f"Very High : "
        f"{distribution['Very High']}"
    )

    print(
        f"High      : "
        f"{distribution['High']}"
    )

    print(
        f"Medium    : "
        f"{distribution['Medium']}"
    )

    print(
        f"Low       : "
        f"{distribution['Low']}"
    )

    print(
        f"\nAverage intelligence score: "
        f"{average}"
    )

    save_dataset(
        enriched_papers
    )

    print("\n" + "=" * 70)

    print(
        "DAY 2 - STEP 5 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Total papers : "
        f"{len(enriched_papers)}"
    )

    print(
        f"Average score: "
        f"{average}"
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