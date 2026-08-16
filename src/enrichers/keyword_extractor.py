import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/enriched_research_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/keyword_enriched_papers.json"
)

TOP_KEYWORDS_PER_PAPER = 10

MIN_DOCUMENT_FREQUENCY = 2

MAX_DOCUMENT_FREQUENCY = 0.95


# =========================================================
# Load dataset
# =========================================================

def load_papers() -> list[dict[str, Any]]:

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):

        raise ValueError(
            "Expected dataset to contain a list."
        )

    return data


# =========================================================
# Clean text
# =========================================================

def clean_text(
    text: Any
) -> str:

    if text is None:
        return ""

    text = str(text)

    # Remove excessive whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# Prepare documents
# =========================================================

def build_documents(
    papers: list[dict[str, Any]]
) -> list[str]:

    documents = []

    for paper in papers:

        title = clean_text(
            paper.get(
                "title",
                ""
            )
        )

        abstract = clean_text(
            paper.get(
                "abstract",
                ""
            )
        )

        # Give title slightly more importance
        document = (
            f"{title} {title} {title} "
            f"{abstract}"
        )

        documents.append(
            document
        )

    return documents


# =========================================================
# Extract keywords
# =========================================================

def extract_keywords(
    papers: list[dict[str, Any]]
) -> list[list[str]]:

    documents = build_documents(
        papers
    )

    print(
        "Building TF-IDF vocabulary..."
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=MIN_DOCUMENT_FREQUENCY,
        max_df=MAX_DOCUMENT_FREQUENCY,
        max_features=20000,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]+\b",
    )

    matrix = vectorizer.fit_transform(
        documents
    )

    feature_names = (
        vectorizer.get_feature_names_out()
    )

    print(
        f"Vocabulary size: "
        f"{len(feature_names)}"
    )

    all_keywords = []

    for paper_index in range(
        matrix.shape[0]
    ):

        row = matrix.getrow(
            paper_index
        )

        scores = row.toarray().flatten()

        ranked_indices = scores.argsort()[
            ::-1
        ]

        keywords = []

        for index in ranked_indices:

            score = scores[index]

            if score <= 0:
                break

            keyword = feature_names[
                index
            ]

            keyword = keyword.strip()

            if not keyword:
                continue

            keywords.append(
                keyword
            )

            if len(keywords) >= TOP_KEYWORDS_PER_PAPER:
                break

        all_keywords.append(
            keywords
        )

    return all_keywords


# =========================================================
# Normalize keyword
# =========================================================

def normalize_keyword(
    keyword: str
) -> str:

    keyword = keyword.lower().strip()

    keyword = re.sub(
        r"\s+",
        " ",
        keyword
    )

    return keyword


# =========================================================
# Calculate global keyword statistics
# =========================================================

def calculate_keyword_statistics(
    papers: list[dict[str, Any]]
) -> dict[str, int]:

    counter = Counter()

    for paper in papers:

        keywords = paper.get(
            "keywords",
            []
        )

        if not isinstance(
            keywords,
            list
        ):
            continue

        for keyword in keywords:

            normalized = normalize_keyword(
                keyword
            )

            if normalized:

                counter[
                    normalized
                ] += 1

    return dict(
        counter.most_common()
    )


# =========================================================
# Save dataset
# =========================================================

def save_dataset(
    papers: list[dict[str, Any]]
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
        "Day 2 - Step 2: Keyword Extraction"
    )
    print("=" * 70)

    print(
        "\nLoading enriched dataset..."
    )

    papers = load_papers()

    print(
        f"Loaded {len(papers)} papers."
    )

    print(
        "\nExtracting research keywords..."
    )

    keyword_lists = extract_keywords(
        papers
    )

    print(
        "\nAdding keywords to papers..."
    )

    for index, paper in enumerate(
        papers
    ):

        paper["keywords"] = (
            keyword_lists[index]
        )

        if (
            (index + 1) % 100 == 0
        ):

            print(
                f"[KEYWORDS] "
                f"{index + 1} papers processed"
            )

    print(
        "\nCalculating keyword statistics..."
    )

    statistics = (
        calculate_keyword_statistics(
            papers
        )
    )

    print(
        "\nTop 20 research keywords:"
    )

    for index, (
        keyword,
        count
    ) in enumerate(
        list(statistics.items())[:20],
        start=1
    ):

        print(
            f"{index:2}. "
            f"{keyword:<35} "
            f"{count}"
        )

    print(
        "\nSaving keyword-enriched dataset..."
    )

    save_dataset(
        papers
    )

    print("\n" + "=" * 70)

    print(
        "DAY 2 - STEP 2 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Total papers : {len(papers)}"
    )

    print(
        f"Output       : {OUTPUT_FILE}"
    )

    print(
        f"Keywords/paper: "
        f"{TOP_KEYWORDS_PER_PAPER}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()