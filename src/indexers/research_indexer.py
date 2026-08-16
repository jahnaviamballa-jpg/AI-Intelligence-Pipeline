import json
import re
from pathlib import Path
from collections import Counter


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/recommended_research_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/research_search_index.json"
)

PROGRESS_INTERVAL = 100


# =========================================================
# Load dataset
# =========================================================

def load_dataset():
    print("\nLoading final Day 2 dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    if not isinstance(papers, list):
        raise ValueError(
            "Dataset must contain a list of papers."
        )

    print(
        f"Loaded {len(papers)} papers."
    )

    return papers


# =========================================================
# Normalize text
# =========================================================

def normalize_text(value):

    if value is None:
        return ""

    if isinstance(value, list):

        value = " ".join(
            str(item)
            for item in value
        )

    value = str(value).lower()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# Tokenize text
# =========================================================

def tokenize(text):

    text = normalize_text(text)

    tokens = re.findall(
        r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*",
        text
    )

    return tokens


# =========================================================
# Build searchable text
# =========================================================

def build_search_text(paper):

    title = normalize_text(
        paper.get("title", "")
    )

    abstract = normalize_text(
        paper.get("abstract", "")
    )

    keywords = normalize_text(
        paper.get("keywords", [])
    )

    topics = normalize_text(
        paper.get("topics", [])
    )

    research_area = normalize_text(
        paper.get("research_area", "")
    )

    research_stage = normalize_text(
        paper.get("research_stage", "")
    )

    detected_trends = normalize_text(
        paper.get("detected_trends", [])
    )

    application_areas = normalize_text(
        paper.get("application_areas", [])
    )

    technical_signals = normalize_text(
        paper.get("technical_signals", [])
    )

    trend_signals = normalize_text(
        paper.get("trend_signals", [])
    )

    return " ".join(
        [
            title,
            title,
            abstract,
            keywords,
            topics,
            research_area,
            research_stage,
            detected_trends,
            application_areas,
            technical_signals,
            trend_signals,
        ]
    ).strip()


# =========================================================
# Build searchable record
# =========================================================

def build_index_record(
    paper,
    index
):

    search_text = build_search_text(
        paper
    )

    tokens = tokenize(
        search_text
    )

    token_frequency = Counter(
        tokens
    )

    return {
        "index": index,

        "paper_url": paper.get(
            "paper_url"
        ),

        "title": paper.get(
            "title"
        ),

        "authors": paper.get(
            "authors",
            []
        ),

        "abstract": paper.get(
            "abstract",
            ""
        ),

        "keywords": paper.get(
            "keywords",
            []
        ),

        "topics": paper.get(
            "topics",
            []
        ),

        "research_area": paper.get(
            "research_area"
        ),

        "research_stage": paper.get(
            "research_stage"
        ),

        "detected_trends": paper.get(
            "detected_trends",
            []
        ),

        "application_areas": paper.get(
            "application_areas",
            []
        ),

        "technical_signals": paper.get(
            "technical_signals",
            []
        ),

        "trend_signals": paper.get(
            "trend_signals",
            []
        ),

        "github_url": paper.get(
            "github_url"
        ),

        "github_stars": paper.get(
            "github_stars"
        ),

        "research_score": paper.get(
            "research_score",
            0
        ),

        "research_intelligence_score": paper.get(
            "research_intelligence_score",
            0
        ),

        "recommendation_score": paper.get(
            "recommendation_score",
            0
        ),

        "recommendation_category": paper.get(
            "recommendation_category"
        ),

        "recommendation_rank": paper.get(
            "recommendation_rank"
        ),

        "published_date": paper.get(
            "published_date"
        ),

        "search_text": search_text,

        "tokens": list(
            token_frequency.keys()
        ),

        "token_frequency": dict(
            token_frequency
        ),

        "token_count": len(tokens),

        "unique_token_count": len(
            token_frequency
        ),
    }


# =========================================================
# Build complete index
# =========================================================

def build_index(papers):

    print(
        "\nBuilding research search index..."
    )

    index_records = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        record = build_index_record(
            paper,
            index
        )

        index_records.append(
            record
        )

        if (
            index % PROGRESS_INTERVAL
            == 0
        ):

            print(
                f"[INDEXED] "
                f"{index} papers"
            )

    return index_records


# =========================================================
# Calculate index statistics
# =========================================================

def calculate_statistics(
    records
):

    total_tokens = 0
    total_unique_tokens = 0

    vocabulary = Counter()

    topic_counter = Counter()

    trend_counter = Counter()

    application_counter = Counter()

    for record in records:

        total_tokens += record.get(
            "token_count",
            0
        )

        total_unique_tokens += record.get(
            "unique_token_count",
            0
        )

        vocabulary.update(
            record.get(
                "tokens",
                []
            )
        )

        for topic in record.get(
            "topics",
            []
        ):

            topic_counter[
                str(topic)
            ] += 1

        for trend in record.get(
            "detected_trends",
            []
        ):

            trend_counter[
                str(trend)
            ] += 1

        for application in record.get(
            "application_areas",
            []
        ):

            application_counter[
                str(application)
            ] += 1

    return {
        "total_papers": len(records),

        "total_tokens": total_tokens,

        "total_unique_tokens": total_unique_tokens,

        "vocabulary_size": len(
            vocabulary
        ),

        "top_terms": vocabulary.most_common(
            25
        ),

        "top_topics": topic_counter.most_common(
            15
        ),

        "top_trends": trend_counter.most_common(
            15
        ),

        "top_applications": application_counter.most_common(
            10
        ),
    }


# =========================================================
# Save index
# =========================================================

def save_index(
    records,
    statistics
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {
        "index_version": "1.0",

        "dataset": (
            "recommended_research_papers"
        ),

        "total_records": len(
            records
        ),

        "statistics": statistics,

        "records": records,
    }

    print(
        "\nSaving research search index..."
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
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
        "Day 3 - Step 1: Research Dataset Indexer"
    )

    print("=" * 70)

    papers = load_dataset()

    records = build_index(
        papers
    )

    statistics = calculate_statistics(
        records
    )

    print(
        "\nIndex statistics:"
    )

    print(
        f"Total papers       : "
        f"{statistics['total_papers']}"
    )

    print(
        f"Total tokens       : "
        f"{statistics['total_tokens']}"
    )

    print(
        f"Vocabulary size    : "
        f"{statistics['vocabulary_size']}"
    )

    print(
        "\nTop search terms:"
    )

    for index, (
        term,
        count
    ) in enumerate(
        statistics["top_terms"][:15],
        start=1
    ):

        print(
            f"{index:2}. "
            f"{term:<25} "
            f"{count}"
        )

    print(
        "\nTop research trends:"
    )

    for index, (
        trend,
        count
    ) in enumerate(
        statistics["top_trends"][:10],
        start=1
    ):

        print(
            f"{index:2}. "
            f"{trend:<30} "
            f"{count}"
        )

    save_index(
        records,
        statistics
    )

    print("\n" + "=" * 70)

    print(
        "DAY 3 - STEP 1 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Indexed papers : "
        f"{len(records)}"
    )

    print(
        "Output         : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()