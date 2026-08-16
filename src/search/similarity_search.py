import json
import math
import re
from collections import Counter
from pathlib import Path


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/recommended_research_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/similarity_index.json"
)

TOP_K = 10

# Common words that should not dominate similarity
STOP_WORDS = {
    "the", "a", "an", "and", "or", "of", "to",
    "in", "for", "on", "with", "by", "from",
    "is", "are", "was", "were", "this", "that",
    "these", "those", "as", "at", "be", "been",
    "being", "into", "through", "using", "used",
    "based", "we", "our", "their", "they",
    "it", "its", "can", "may", "more", "than",
    "which", "also", "such", "not", "but",
}


# =========================================================
# Load dataset
# =========================================================

def load_dataset():

    print(
        "\nLoading recommendation dataset..."
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
# Tokenize
# =========================================================

def tokenize(text):

    text = normalize_text(
        text
    )

    tokens = text.split()

    return [
        token
        for token in tokens
        if (
            len(token) > 2
            and token not in STOP_WORDS
        )
    ]


# =========================================================
# Build paper text
# =========================================================

def build_paper_text(paper):

    fields = [

        paper.get(
            "title",
            ""
        ),

        paper.get(
            "abstract",
            ""
        ),

        paper.get(
            "keywords",
            []
        ),

        paper.get(
            "topics",
            []
        ),

        paper.get(
            "research_area",
            ""
        ),

        paper.get(
            "detected_trends",
            []
        ),

        paper.get(
            "technical_signals",
            []
        ),

        paper.get(
            "application_areas",
            []
        ),
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

    return " ".join(parts)


# =========================================================
# Build TF-IDF vocabulary
# =========================================================

def build_vocabulary(
    token_lists
):

    document_frequency = Counter()

    for tokens in token_lists:

        unique_tokens = set(
            tokens
        )

        for token in unique_tokens:

            document_frequency[
                token
            ] += 1

    return document_frequency


# =========================================================
# Calculate TF-IDF vector
# =========================================================

def calculate_tfidf(
    tokens,
    document_frequency,
    total_documents
):

    term_frequency = Counter(
        tokens
    )

    vector = {}

    for term, frequency in (
        term_frequency.items()
    ):

        df = document_frequency.get(
            term,
            0
        )

        if df == 0:
            continue

        tf = 1 + math.log(
            frequency
        )

        idf = math.log(
            (
                total_documents + 1
            )
            /
            (
                df + 1
            )
        ) + 1

        vector[term] = (
            tf * idf
        )

    return vector


# =========================================================
# Cosine similarity
# =========================================================

def cosine_similarity(
    vector_a,
    vector_b
):

    if not vector_a or not vector_b:

        return 0.0

    common_terms = (
        set(vector_a)
        &
        set(vector_b)
    )

    if not common_terms:

        return 0.0

    dot_product = sum(
        vector_a[term]
        *
        vector_b[term]
        for term in common_terms
    )

    magnitude_a = math.sqrt(
        sum(
            value * value
            for value in vector_a.values()
        )
    )

    magnitude_b = math.sqrt(
        sum(
            value * value
            for value in vector_b.values()
        )
    )

    if (
        magnitude_a == 0
        or magnitude_b == 0
    ):

        return 0.0

    return (
        dot_product
        /
        (
            magnitude_a
            *
            magnitude_b
        )
    )


# =========================================================
# Build similarity index
# =========================================================

def build_similarity_index(
    papers
):

    print(
        "\nBuilding similarity vectors..."
    )

    token_lists = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        text = build_paper_text(
            paper
        )

        tokens = tokenize(
            text
        )

        token_lists.append(
            tokens
        )

        if index % 100 == 0:

            print(
                f"[TEXT] "
                f"{index} papers processed"
            )

    document_frequency = (
        build_vocabulary(
            token_lists
        )
    )

    print(
        f"\nVocabulary size: "
        f"{len(document_frequency)}"
    )

    vectors = []

    total_documents = len(
        papers
    )

    print(
        "\nCalculating TF-IDF vectors..."
    )

    for index, tokens in enumerate(
        token_lists,
        start=1
    ):

        vector = calculate_tfidf(
            tokens,
            document_frequency,
            total_documents
        )

        vectors.append(
            vector
        )

        if index % 100 == 0:

            print(
                f"[VECTORS] "
                f"{index} papers processed"
            )

    return vectors


# =========================================================
# Find similar papers
# =========================================================

def find_similar_papers(
    paper_index,
    papers,
    vectors,
    top_k=TOP_K
):

    if (
        paper_index < 0
        or paper_index >= len(papers)
    ):

        return []

    target_vector = vectors[
        paper_index
    ]

    similarities = []

    for index, vector in enumerate(
        vectors
    ):

        if index == paper_index:

            continue

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

                "similarity_score": round(
                    score * 100,
                    4
                ),
            }
        )

    return results


# =========================================================
# Save similarity index
# =========================================================

def save_index(
    papers,
    vectors
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\nSaving similarity index..."
    )

    data = {

        "total_papers": len(
            papers
        ),

        "vector_count": len(
            vectors
        ),

        "method": "TF-IDF cosine similarity",

        "papers": []
    }

    for index, (
        paper,
        vector
    ) in enumerate(
        zip(
            papers,
            vectors
        )
    ):

        data["papers"].append(
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

                "vector": vector,
            }
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# Test similarity engine
# =========================================================

def run_test(
    papers,
    vectors
):

    print(
        "\nTesting similarity engine..."
    )

    if not papers:

        return

    test_index = 0

    test_paper = papers[
        test_index
    ]

    print(
        "\nReference paper:"
    )

    print(
        test_paper.get(
            "title"
        )
    )

    results = find_similar_papers(
        test_index,
        papers,
        vectors,
        TOP_K
    )

    print(
        "\nTop similar papers:"
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n#{rank} "
            f"[Similarity: "
            f"{result['similarity_score']:.2f}]"
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
            f"URL: "
            f"{result['paper_url']}"
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
        "Day 3 - Step 3: "
        "Research Similarity Engine"
    )

    print("=" * 70)

    papers = load_dataset()

    vectors = build_similarity_index(
        papers
    )

    save_index(
        papers,
        vectors
    )

    run_test(
        papers,
        vectors
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "DAY 3 - STEP 3 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Indexed papers : "
        f"{len(papers)}"
    )

    print(
        f"Vocabulary     : "
        f"{sum(len(v) for v in vectors)}"
    )

    print(
        "Output         : "
        f"{OUTPUT_FILE}"
    )

    print(
        "=" * 70
    )


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()