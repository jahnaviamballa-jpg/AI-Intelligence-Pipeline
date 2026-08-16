import json
import re
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

OUTPUT_FILE = Path(
    "data/processed/research_api_metadata.json"
)


# =========================================================
# Load dataset
# =========================================================

def load_dataset():

    print(
        "\nLoading research dataset..."
    )

    with DATASET_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    print(
        f"Loaded {len(papers)} papers."
    )

    return papers


# =========================================================
# Load similarity index
# =========================================================

def load_similarity_index():

    print(
        "\nLoading similarity index..."
    )

    with SIMILARITY_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        similarity_data = json.load(
            file
        )

    print(
        f"Loaded similarity index for "
        f"{similarity_data.get('total_papers', 0)} papers."
    )

    return similarity_data


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
        r"[^a-z0-9\s-]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# Build searchable text
# =========================================================

def build_search_text(paper):

    fields = [
        paper.get("title", ""),
        paper.get("abstract", ""),
        paper.get("keywords", []),
        paper.get("topics", []),
        paper.get("research_area", ""),
        paper.get("research_stage", ""),
        paper.get("detected_trends", []),
        paper.get("trend_signals", []),
        paper.get("technical_signals", []),
        paper.get("application_areas", []),
        paper.get("application_signals", []),
    ]

    parts = []

    for field in fields:

        if isinstance(field, list):

            parts.extend(
                str(item)
                for item in field
            )

        else:

            parts.append(
                str(field)
            )

    return normalize_text(
        " ".join(parts)
    )


# =========================================================
# Query tokenization
# =========================================================

def tokenize_query(query):

    query = normalize_text(
        query
    )

    return [
        token
        for token in query.split()
        if len(token) > 2
    ]


# =========================================================
# Calculate keyword relevance
# =========================================================

def calculate_keyword_score(
    paper,
    query_tokens
):

    if not query_tokens:
        return 0.0

    text = build_search_text(
        paper
    )

    title = normalize_text(
        paper.get("title", "")
    )

    score = 0.0

    for token in query_tokens:

        # Strongest signal: title
        if token in title:
            score += 5.0

        # General paper content
        if token in text:
            score += 1.0

    return score


# =========================================================
# Research quality score
# =========================================================

def get_quality_score(paper):

    value = paper.get(
        "research_score",
        0
    )

    try:
        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# =========================================================
# Intelligence score
# =========================================================

def get_intelligence_score(
    paper
):

    value = paper.get(
        "research_intelligence_score",
        0
    )

    try:
        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# =========================================================
# Recommendation score
# =========================================================

def get_recommendation_score(
    paper
):

    value = paper.get(
        "recommendation_score",
        0
    )

    try:
        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# =========================================================
# Search papers
# =========================================================

def search_papers(
    papers,
    query,
    top_k=10
):

    query_tokens = tokenize_query(
        query
    )

    if not query_tokens:
        return []

    scored_results = []

    for index, paper in enumerate(
        papers
    ):

        keyword_score = (
            calculate_keyword_score(
                paper,
                query_tokens
            )
        )

        if keyword_score <= 0:
            continue

        quality_score = (
            get_quality_score(
                paper
            )
        )

        intelligence_score = (
            get_intelligence_score(
                paper
            )
        )

        recommendation_score = (
            get_recommendation_score(
                paper
            )
        )

        # Combined ranking score
        final_score = (
            keyword_score
            * 5.0
            +
            quality_score
            * 0.15
            +
            intelligence_score
            * 0.15
            +
            recommendation_score
            * 0.10
        )

        scored_results.append(
            (
                index,
                final_score
            )
        )

    scored_results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for index, score in (
        scored_results[:top_k]
    ):

        paper = papers[
            index
        ]

        results.append(
            {
                "rank": len(results) + 1,

                "paper_index": index,

                "title": paper.get(
                    "title"
                ),

                "paper_url": paper.get(
                    "paper_url"
                ),

                "research_area": paper.get(
                    "research_area"
                ),

                "research_stage": paper.get(
                    "research_stage"
                ),

                "recommendation_category":
                    paper.get(
                        "recommendation_category"
                    ),

                "research_score":
                    paper.get(
                        "research_score"
                    ),

                "intelligence_score":
                    paper.get(
                        "research_intelligence_score"
                    ),

                "recommendation_score":
                    paper.get(
                        "recommendation_score"
                    ),

                "search_score":
                    round(
                        score,
                        4
                    ),
            }
        )

    return results


# =========================================================
# Filter by research area
# =========================================================

def filter_by_area(
    papers,
    area
):

    area = normalize_text(
        area
    )

    results = []

    for index, paper in enumerate(
        papers
    ):

        paper_area = normalize_text(
            paper.get(
                "research_area",
                ""
            )
        )

        if area in paper_area:

            results.append(
                {
                    "paper_index": index,

                    "title": paper.get(
                        "title"
                    ),

                    "paper_url": paper.get(
                        "paper_url"
                    ),

                    "research_area": paper.get(
                        "research_area"
                    ),

                    "research_stage": paper.get(
                        "research_stage"
                    ),

                    "recommendation_score":
                        paper.get(
                            "recommendation_score"
                        ),
                }
            )

    return results


# =========================================================
# Filter by research stage
# =========================================================

def filter_by_stage(
    papers,
    stage
):

    stage = normalize_text(
        stage
    )

    results = []

    for index, paper in enumerate(
        papers
    ):

        paper_stage = normalize_text(
            paper.get(
                "research_stage",
                ""
            )
        )

        if stage == paper_stage:

            results.append(
                {
                    "paper_index": index,

                    "title": paper.get(
                        "title"
                    ),

                    "paper_url": paper.get(
                        "paper_url"
                    ),

                    "research_area": paper.get(
                        "research_area"
                    ),

                    "research_stage": paper.get(
                        "research_stage"
                    ),

                    "recommendation_score":
                        paper.get(
                            "recommendation_score"
                        ),
                }
            )

    return results


# =========================================================
# Find similar papers
# =========================================================

def find_similar_papers(
    paper_index,
    papers,
    similarity_data,
    top_k=10
):

    similarity_papers = (
        similarity_data.get(
            "papers",
            []
        )
    )

    if (
        paper_index < 0
        or paper_index >= len(
            similarity_papers
        )
    ):

        return []

    target = similarity_papers[
        paper_index
    ]

    target_vector = target.get(
        "vector",
        {}
    )

    if not target_vector:
        return []

    similarities = []

    # Import locally so the API remains
    # lightweight.
    from src.search.similarity_search import (
        cosine_similarity
    )

    for index, item in enumerate(
        similarity_papers
    ):

        if index == paper_index:
            continue

        vector = item.get(
            "vector",
            {}
        )

        score = cosine_similarity(
            target_vector,
            vector
        )

        similarities.append(
            (
                index,
                score
            )
        )

    similarities.sort(
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for index, score in similarities[
        :top_k
    ]:

        paper = papers[
            index
        ]

        results.append(
            {
                "rank": len(results) + 1,

                "paper_index": index,

                "title": paper.get(
                    "title"
                ),

                "paper_url": paper.get(
                    "paper_url"
                ),

                "research_area": paper.get(
                    "research_area"
                ),

                "research_stage": paper.get(
                    "research_stage"
                ),

                "similarity_score":
                    round(
                        score * 100,
                        4
                    ),
            }
        )

    return results


# =========================================================
# Get top recommendations
# =========================================================

def get_top_recommendations(
    papers,
    top_k=10
):

    ranked = []

    for index, paper in enumerate(
        papers
    ):

        score = (
            get_recommendation_score(
                paper
            )
        )

        ranked.append(
            (
                index,
                score
            )
        )

    ranked.sort(
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for index, score in ranked[
        :top_k
    ]:

        paper = papers[
            index
        ]

        results.append(
            {
                "rank": len(results) + 1,

                "paper_index": index,

                "title": paper.get(
                    "title"
                ),

                "paper_url": paper.get(
                    "paper_url"
                ),

                "research_area": paper.get(
                    "research_area"
                ),

                "research_stage": paper.get(
                    "research_stage"
                ),

                "recommendation_score":
                    score,

                "recommendation_category":
                    paper.get(
                        "recommendation_category"
                    ),
            }
        )

    return results


# =========================================================
# API capabilities
# =========================================================

def build_api_metadata(
    papers,
    similarity_data
):

    research_areas = sorted(
        {
            str(
                paper.get(
                    "research_area"
                )
            )
            for paper in papers
            if paper.get(
                "research_area"
            )
        }
    )

    research_stages = sorted(
        {
            str(
                paper.get(
                    "research_stage"
                )
            )
            for paper in papers
            if paper.get(
                "research_stage"
            )
        }
    )

    return {
        "dataset": {
            "total_papers": len(
                papers
            ),

            "similarity_vectors":
                similarity_data.get(
                    "vector_count",
                    0
                ),
        },

        "capabilities": [
            "keyword_search",
            "research_area_filter",
            "research_stage_filter",
            "paper_similarity",
            "recommendation_ranking",
        ],

        "research_areas":
            research_areas,

        "research_stages":
            research_stages,
    }


# =========================================================
# Save API metadata
# =========================================================

def save_metadata(
    metadata
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
            metadata,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nAPI metadata saved to:"
    )

    print(
        OUTPUT_FILE
    )


# =========================================================
# Demonstration
# =========================================================

def run_demo(
    papers,
    similarity_data
):

    print(
        "\n" + "-" * 70
    )

    print(
        "API DEMONSTRATION"
    )

    print(
        "-" * 70
    )

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    query = "LLM reasoning"

    print(
        f"\n1. Search: {query}"
    )

    results = search_papers(
        papers,
        query,
        5
    )

    for result in results:

        print(
            f"\n#{result['rank']} "
            f"[{result['search_score']:.2f}]"
        )

        print(
            result["title"]
        )

        print(
            f"Area: "
            f"{result['research_area']}"
        )

    # -----------------------------------------------------
    # Area filter
    # -----------------------------------------------------

    print(
        "\n2. Research area filter:"
    )

    area_results = filter_by_area(
        papers,
        "Agentic AI"
    )

    print(
        f"Agentic AI papers: "
        f"{len(area_results)}"
    )

    # -----------------------------------------------------
    # Emerging papers
    # -----------------------------------------------------

    print(
        "\n3. Emerging research:"
    )

    emerging_results = (
        filter_by_stage(
            papers,
            "Emerging"
        )
    )

    print(
        f"Emerging papers: "
        f"{len(emerging_results)}"
    )

    # -----------------------------------------------------
    # Similarity
    # -----------------------------------------------------

    print(
        "\n4. Similarity search:"
    )

    similar_results = (
        find_similar_papers(
            0,
            papers,
            similarity_data,
            5
        )
    )

    for result in similar_results:

        print(
            f"\n#{result['rank']} "
            f"[{result['similarity_score']:.2f}]"
        )

        print(
            result["title"]
        )

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    print(
        "\n5. Top recommendations:"
    )

    recommendations = (
        get_top_recommendations(
            papers,
            5
        )
    )

    for result in recommendations:

        print(
            f"\n#{result['rank']} "
            f"[{result['recommendation_score']:.2f}]"
        )

        print(
            result["title"]
        )

        print(
            f"Category: "
            f"{result['recommendation_category']}"
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
        "Day 3 - Step 4: "
        "Unified Research Intelligence API"
    )

    print("=" * 70)

    papers = load_dataset()

    similarity_data = (
        load_similarity_index()
    )

    metadata = build_api_metadata(
        papers,
        similarity_data
    )

    save_metadata(
        metadata
    )

    run_demo(
        papers,
        similarity_data
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "DAY 3 - STEP 4 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Research papers : "
        f"{len(papers)}"
    )

    print(
        "API capabilities: "
        f"{len(metadata['capabilities'])}"
    )

    print(
        "Metadata output : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()