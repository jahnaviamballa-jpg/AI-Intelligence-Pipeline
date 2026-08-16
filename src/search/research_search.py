import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


# =========================================================
# Configuration
# =========================================================

INDEX_FILE = Path(
    "data/processed/research_search_index.json"
)

OUTPUT_FILE = Path(
    "data/processed/search_engine_metadata.json"
)

TOP_K = 10


# =========================================================
# Stop words
# =========================================================

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be",
    "by", "for", "from", "in", "into", "is",
    "it", "of", "on", "or", "that", "the",
    "their", "this", "to", "was", "were",
    "with", "using", "we", "our", "can",
    "may", "has", "have", "had", "but",
    "not", "than", "these", "those", "such",
    "which", "how", "what", "when", "where",
    "who", "why", "while", "through", "based",
    "also", "more", "new", "used", "use"
}


# =========================================================
# Load index
# =========================================================

def load_index():

    print("\nLoading research search index...")

    if not INDEX_FILE.exists():

        raise FileNotFoundError(
            f"Search index not found: {INDEX_FILE}"
        )

    with INDEX_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    records = data.get(
        "records",
        []
    )

    if not records:

        raise ValueError(
            "Search index contains no records."
        )

    print(
        f"Loaded {len(records)} indexed papers."
    )

    return records


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
        r"[^a-z0-9\s\-]",
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
# Tokenize query
# =========================================================

def tokenize_query(query):

    text = normalize_text(
        query
    )

    tokens = re.findall(
        r"[a-z0-9]+(?:-[a-z0-9]+)*",
        text
    )

    tokens = [
        token
        for token in tokens
        if token not in STOP_WORDS
        and len(token) > 1
    ]

    return tokens


# =========================================================
# Build document text
# =========================================================

def get_document_text(record):

    return normalize_text(
        record.get(
            "search_text",
            ""
        )
    )


# =========================================================
# Build inverted index
# =========================================================

def build_inverted_index(records):

    print(
        "\nBuilding inverted search index..."
    )

    inverted_index = defaultdict(set)

    document_frequency = Counter()

    for record in records:

        record_index = record.get(
            "index"
        )

        text = get_document_text(
            record
        )

        tokens = set(
            tokenize_query(
                text
            )
        )

        for token in tokens:

            inverted_index[
                token
            ].add(
                record_index
            )

        for token in tokens:

            document_frequency[
                token
            ] += 1

    print(
        f"Search vocabulary: "
        f"{len(inverted_index)}"
    )

    return (
        inverted_index,
        document_frequency
    )


# =========================================================
# Calculate IDF
# =========================================================

def calculate_idf(
    total_documents,
    document_frequency
):

    idf = {}

    for token, frequency in (
        document_frequency.items()
    ):

        idf[token] = math.log(
            (
                total_documents + 1
            )
            /
            (
                frequency + 1
            )
        ) + 1

    return idf


# =========================================================
# Build field text
# =========================================================

def get_field_tokens(
    record
):

    fields = {}

    fields["title"] = tokenize_query(
        record.get(
            "title",
            ""
        )
    )

    fields["abstract"] = tokenize_query(
        record.get(
            "abstract",
            ""
        )
    )

    fields["keywords"] = tokenize_query(
        record.get(
            "keywords",
            []
        )
    )

    fields["topics"] = tokenize_query(
        record.get(
            "topics",
            []
        )
    )

    fields["research_area"] = tokenize_query(
        record.get(
            "research_area",
            ""
        )
    )

    fields["trends"] = tokenize_query(
        record.get(
            "detected_trends",
            []
        )
    )

    fields["applications"] = tokenize_query(
        record.get(
            "application_areas",
            []
        )
    )

    fields["technical"] = tokenize_query(
        record.get(
            "technical_signals",
            []
        )
    )

    return fields


# =========================================================
# Calculate field match score
# =========================================================

def calculate_field_score(
    query_tokens,
    record
):

    fields = get_field_tokens(
        record
    )

    weights = {
        "title": 6.0,
        "keywords": 5.0,
        "topics": 4.5,
        "research_area": 4.0,
        "trends": 4.0,
        "applications": 3.5,
        "technical": 3.0,
        "abstract": 1.5,
    }

    score = 0.0

    for field_name, field_tokens in (
        fields.items()
    ):

        if not field_tokens:
            continue

        field_counter = Counter(
            field_tokens
        )

        matches = 0

        for token in query_tokens:

            if token in field_counter:

                matches += min(
                    field_counter[token],
                    3
                )

        if matches:

            score += (
                matches
                *
                weights[field_name]
            )

    return score


# =========================================================
# Calculate TF-IDF score
# =========================================================

def calculate_tfidf_score(
    query_tokens,
    record,
    idf
):

    document_tokens = tokenize_query(
        get_document_text(
            record
        )
    )

    if not document_tokens:
        return 0.0

    document_counter = Counter(
        document_tokens
    )

    score = 0.0

    for token in query_tokens:

        if token not in document_counter:
            continue

        term_frequency = (
            document_counter[token]
            /
            len(document_tokens)
        )

        score += (
            term_frequency
            *
            idf.get(
                token,
                1.0
            )
        )

    return score


# =========================================================
# Calculate exact phrase score
# =========================================================

def calculate_phrase_score(
    query,
    record
):

    normalized_query = normalize_text(
        query
    )

    if not normalized_query:
        return 0.0

    title = normalize_text(
        record.get(
            "title",
            ""
        )
    )

    abstract = normalize_text(
        record.get(
            "abstract",
            ""
        )
    )

    keywords = normalize_text(
        record.get(
            "keywords",
            []
        )
    )

    score = 0.0

    if normalized_query in title:
        score += 20.0

    if normalized_query in keywords:
        score += 15.0

    if normalized_query in abstract:
        score += 5.0

    return score


# =========================================================
# Calculate quality boost
# =========================================================

def calculate_quality_boost(
    record
):

    research_score = float(
        record.get(
            "research_score",
            0
        ) or 0
    )

    intelligence_score = float(
        record.get(
            "research_intelligence_score",
            0
        ) or 0
    )

    recommendation_score = float(
        record.get(
            "recommendation_score",
            0
        ) or 0
    )

    quality = (
        research_score * 0.25
        +
        intelligence_score * 0.35
        +
        recommendation_score * 0.40
    )

    return quality / 10.0


# =========================================================
# Calculate GitHub boost
# =========================================================

def calculate_github_boost(
    record
):

    stars = record.get(
        "github_stars"
    )

    if stars is None:
        return 0.0

    try:

        stars = float(
            stars
        )

    except (
        ValueError,
        TypeError
    ):

        return 0.0

    if stars <= 0:
        return 0.0

    return min(
        math.log10(
            stars + 1
        ) * 2.0,
        10.0
    )


# =========================================================
# Score one document
# =========================================================

def score_document(
    query,
    query_tokens,
    record,
    idf
):

    field_score = calculate_field_score(
        query_tokens,
        record
    )

    tfidf_score = calculate_tfidf_score(
        query_tokens,
        record,
        idf
    )

    phrase_score = calculate_phrase_score(
        query,
        record
    )

    quality_boost = calculate_quality_boost(
        record
    )

    github_boost = calculate_github_boost(
        record
    )

    # Weighted ranking
    final_score = (
        field_score
        +
        (tfidf_score * 20.0)
        +
        phrase_score
        +
        quality_boost
        +
        github_boost
    )

    return final_score


# =========================================================
# Search
# =========================================================

def search(
    query,
    records,
    inverted_index,
    idf,
    top_k=TOP_K
):

    query_tokens = tokenize_query(
        query
    )

    if not query_tokens:

        return []

    # -----------------------------------------------------
    # Candidate retrieval
    # -----------------------------------------------------

    candidate_ids = set()

    for token in query_tokens:

        candidate_ids.update(
            inverted_index.get(
                token,
                set()
            )
        )

    # If no exact token matches,
    # fall back to all documents.

    if not candidate_ids:

        candidate_ids = {
            record.get("index")
            for record in records
        }

    record_lookup = {
        record.get("index"): record
        for record in records
    }

    results = []

    for record_id in candidate_ids:

        record = record_lookup.get(
            record_id
        )

        if not record:
            continue

        score = score_document(
            query,
            query_tokens,
            record,
            idf
        )

        if score <= 0:
            continue

        results.append(
            (
                score,
                record
            )
        )

    results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    output = []

    for rank, (
        score,
        record
    ) in enumerate(
        results[:top_k],
        start=1
    ):

        output.append(
            {
                "rank": rank,

                "score": round(
                    score,
                    4
                ),

                "title": record.get(
                    "title"
                ),

                "paper_url": record.get(
                    "paper_url"
                ),

                "authors": record.get(
                    "authors",
                    []
                ),

                "topics": record.get(
                    "topics",
                    []
                ),

                "research_area": record.get(
                    "research_area"
                ),

                "research_stage": record.get(
                    "research_stage"
                ),

                "detected_trends": record.get(
                    "detected_trends",
                    []
                ),

                "recommendation_score": record.get(
                    "recommendation_score",
                    0
                ),

                "recommendation_category": record.get(
                    "recommendation_category"
                ),

                "github_url": record.get(
                    "github_url"
                ),

                "github_stars": record.get(
                    "github_stars"
                ),
            }
        )

    return output


# =========================================================
# Save search metadata
# =========================================================

def save_metadata(
    vocabulary_size,
    document_count
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata = {
        "search_engine_version": "1.0",

        "document_count": document_count,

        "vocabulary_size": vocabulary_size,

        "ranking_method": (
            "Field-weighted TF-IDF + "
            "phrase matching + "
            "research quality + "
            "GitHub popularity"
        ),

        "searchable_fields": [
            "title",
            "abstract",
            "keywords",
            "topics",
            "research_area",
            "detected_trends",
            "application_areas",
            "technical_signals",
        ],
    }

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


# =========================================================
# Interactive search
# =========================================================

def interactive_search(
    records,
    inverted_index,
    idf
):

    print("\n" + "=" * 70)

    print(
        "Research Search Engine"
    )

    print("=" * 70)

    print(
        "Type a research query."
    )

    print(
        "Examples:"
    )

    print(
        "  LLM reasoning"
    )

    print(
        "  AI agents for software engineering"
    )

    print(
        "  multimodal AI"
    )

    print(
        "  reinforcement learning robotics"
    )

    print(
        "\nType 'exit' to stop."
    )

    while True:

        try:

            query = input(
                "\nSearch> "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt
        ):

            print(
                "\nExiting search engine."
            )

            break

        if query.lower() == "exit":
            break

        if not query:
            continue

        results = search(
            query,
            records,
            inverted_index,
            idf,
            TOP_K
        )

        print(
            "\n"
            + "-" * 70
        )

        print(
            f"Results for: {query}"
        )

        print(
            "-" * 70
        )

        if not results:

            print(
                "No relevant papers found."
            )

            continue

        for result in results:

            print(
                f"\n#{result['rank']} "
                f"[Score: "
                f"{result['score']}]"
            )

            print(
                f"Title: "
                f"{result['title']}"
            )

            print(
                f"Research area: "
                f"{result['research_area']}"
            )

            print(
                f"Stage: "
                f"{result['research_stage']}"
            )

            print(
                f"Recommendation: "
                f"{result['recommendation_category']}"
            )

            print(
                f"URL: "
                f"{result['paper_url']}"
            )

            if result.get(
                "github_url"
            ):

                print(
                    f"GitHub: "
                    f"{result['github_url']}"
                )

                print(
                    f"GitHub stars: "
                    f"{result['github_stars']}"
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
        "Day 3 - Step 2: Research Search Engine"
    )

    print("=" * 70)

    records = load_index()

    (
        inverted_index,
        document_frequency
    ) = build_inverted_index(
        records
    )

    idf = calculate_idf(
        len(records),
        document_frequency
    )

    save_metadata(
        len(inverted_index),
        len(records)
    )

    print(
        "\nSearch engine initialized successfully."
    )

    print(
        f"Documents : {len(records)}"
    )

    print(
        f"Vocabulary: {len(inverted_index)}"
    )

    print(
        "\nStarting interactive search..."
    )

    interactive_search(
        records,
        inverted_index,
        idf
    )

    print("\n" + "=" * 70)

    print(
        "DAY 3 - STEP 2 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Indexed papers : "
        f"{len(records)}"
    )

    print(
        f"Search terms   : "
        f"{len(inverted_index)}"
    )

    print(
        "Search metadata: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()