import json
from pathlib import Path


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/topic_enriched_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/scored_research_papers.json"
)

PROGRESS_INTERVAL = 100


# =========================================================
# Load dataset
# =========================================================

def load_dataset():
    print("Loading topic-enriched dataset...")

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
# Score GitHub information
# =========================================================

def calculate_github_score(paper):
    score = 0

    github_url = paper.get(
        "github_url"
    )

    github_stars = paper.get(
        "github_stars"
    )

    # Repository exists
    if github_url:
        score += 10

    # Repository popularity
    if github_stars is not None:

        if github_stars >= 1000:
            score += 20

        elif github_stars >= 500:
            score += 17

        elif github_stars >= 100:
            score += 14

        elif github_stars >= 50:
            score += 12

        elif github_stars >= 10:
            score += 8

        else:
            score += 5

    return min(score, 30)


# =========================================================
# Score metadata completeness
# =========================================================

def calculate_metadata_score(paper):
    score = 0

    title = paper.get("title")
    authors = paper.get("authors")
    paper_url = paper.get("paper_url")
    published_date = paper.get(
        "published_date"
    )
    summary = paper.get("summary")

    if title:
        score += 5

    if authors:
        score += 5

    if paper_url:
        score += 5

    if published_date:
        score += 5

    if summary:
        score += 5

    return score


# =========================================================
# Score keywords
# =========================================================

def calculate_keyword_score(paper):
    keywords = paper.get(
        "keywords",
        []
    )

    if not isinstance(
        keywords,
        list
    ):
        return 0

    count = len(keywords)

    if count >= 10:
        return 15

    if count >= 7:
        return 12

    if count >= 5:
        return 9

    if count >= 3:
        return 6

    if count >= 1:
        return 3

    return 0


# =========================================================
# Score research topic
# =========================================================

def calculate_topic_score(paper):
    topic = paper.get(
        "topic"
    )

    if not topic:
        return 0

    # More specific research topics receive
    # a slightly higher score.
    general_topics = {
        "General AI/ML",
        "Machine Learning",
    }

    if topic in general_topics:
        return 7

    return 10


# =========================================================
# Calculate total research score
# =========================================================

def calculate_research_score(paper):

    github_score = (
        calculate_github_score(
            paper
        )
    )

    metadata_score = (
        calculate_metadata_score(
            paper
        )
    )

    keyword_score = (
        calculate_keyword_score(
            paper
        )
    )

    topic_score = (
        calculate_topic_score(
            paper
        )
    )

    total_score = (
        github_score
        + metadata_score
        + keyword_score
        + topic_score
    )

    # Maximum:
    #
    # GitHub      = 30
    # Metadata    = 25
    # Keywords    = 15
    # Topic       = 10
    #
    # Total       = 80
    #
    # Normalize to 100.

    normalized_score = round(
        (total_score / 80) * 100,
        2
    )

    return {
        "research_score": normalized_score,
        "github_score": github_score,
        "metadata_score": metadata_score,
        "keyword_score": keyword_score,
        "topic_score": topic_score,
    }


# =========================================================
# Quality label
# =========================================================

def get_quality_label(score):

    if score >= 75:
        return "High"

    if score >= 50:
        return "Medium"

    return "Low"


# =========================================================
# Score all papers
# =========================================================

def score_papers(papers):

    print("\nCalculating research quality scores...")

    scored_papers = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        scores = calculate_research_score(
            paper
        )

        paper.update(
            scores
        )

        paper["quality_label"] = (
            get_quality_label(
                scores["research_score"]
            )
        )

        scored_papers.append(
            paper
        )

        if (
            index % PROGRESS_INTERVAL
            == 0
        ):
            print(
                f"[SCORED] "
                f"{index} papers"
            )

    return scored_papers


# =========================================================
# Statistics
# =========================================================

def calculate_statistics(papers):

    high = 0
    medium = 0
    low = 0

    total_score = 0

    for paper in papers:

        score = paper.get(
            "research_score",
            0
        )

        total_score += score

        label = paper.get(
            "quality_label"
        )

        if label == "High":
            high += 1

        elif label == "Medium":
            medium += 1

        else:
            low += 1

    average_score = round(
        total_score / len(papers),
        2
    ) if papers else 0

    return {
        "high": high,
        "medium": medium,
        "low": low,
        "average": average_score,
    }


# =========================================================
# Save dataset
# =========================================================

def save_dataset(papers):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\nSaving scored dataset..."
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
        "Day 2 - Step 4: Research Quality Scoring"
    )
    print("=" * 70)

    papers = load_dataset()

    scored_papers = score_papers(
        papers
    )

    statistics = (
        calculate_statistics(
            scored_papers
        )
    )

    print("\nResearch quality distribution:")

    print(
        f"High quality   : "
        f"{statistics['high']}"
    )

    print(
        f"Medium quality : "
        f"{statistics['medium']}"
    )

    print(
        f"Low quality    : "
        f"{statistics['low']}"
    )

    print(
        f"Average score  : "
        f"{statistics['average']}"
    )

    save_dataset(
        scored_papers
    )

    print("\n" + "=" * 70)
    print(
        "DAY 2 - STEP 4 COMPLETED"
    )
    print("=" * 70)

    print(
        f"Total papers : "
        f"{len(scored_papers)}"
    )

    print(
        f"Average score: "
        f"{statistics['average']}"
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