import json
import re
from pathlib import Path
from typing import Any


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/keyword_enriched_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/topic_enriched_papers.json"
)

MIN_TOPIC_SCORE = 1


# =========================================================
# Topic vocabulary
# =========================================================

TOPIC_KEYWORDS = {

    "AI Agents": [
        "agent",
        "agents",
        "agentic",
        "agent-based",
        "multi-agent",
        "autonomous agent",
        "tool use",
        "tool-use",
        "agentic workflow",
        "agentic system",
    ],

    "Large Language Models": [
        "llm",
        "llms",
        "large language model",
        "large language models",
        "language model",
        "language models",
        "transformer",
        "transformers",
        "instruction tuning",
        "instruction-following",
    ],

    "Natural Language Processing": [
        "nlp",
        "natural language processing",
        "text classification",
        "text generation",
        "named entity",
        "information extraction",
        "sentiment analysis",
        "question answering",
        "machine translation",
        "semantic",
        "language understanding",
    ],

    "Computer Vision": [
        "computer vision",
        "image classification",
        "image generation",
        "object detection",
        "image segmentation",
        "visual recognition",
        "vision transformer",
        "visual",
        "video understanding",
        "image",
        "images",
    ],

    "Multimodal AI": [
        "multimodal",
        "multi-modal",
        "vision-language",
        "vision language",
        "audio-visual",
        "image-text",
        "text-image",
        "vision and language",
        "omni-modal",
    ],

    "Generative AI": [
        "generative ai",
        "generative model",
        "generative models",
        "generation",
        "diffusion",
        "diffusion model",
        "diffusion models",
        "text generation",
        "image generation",
        "synthetic data",
    ],

    "Reinforcement Learning": [
        "reinforcement learning",
        "reinforcement",
        "rl",
        "policy learning",
        "reward",
        "reward model",
        "reward modeling",
        "offline reinforcement",
        "online reinforcement",
    ],

    "Machine Learning": [
        "machine learning",
        "deep learning",
        "learning algorithm",
        "learning algorithms",
        "supervised learning",
        "self-supervised",
        "semi-supervised",
        "representation learning",
        "meta-learning",
    ],

    "Optimization": [
        "optimization",
        "optimizer",
        "optimisation",
        "gradient descent",
        "hyperparameter",
        "hyperparameter optimization",
        "parameter optimization",
        "search algorithm",
    ],

    "AI Safety": [
        "ai safety",
        "safety",
        "alignment",
        "ai alignment",
        "robustness",
        "trustworthy ai",
        "responsible ai",
        "red teaming",
        "jailbreak",
        "adversarial",
        "security",
    ],

    "AI Evaluation": [
        "evaluation",
        "benchmark",
        "benchmarks",
        "evaluation framework",
        "evaluation metric",
        "metrics",
        "benchmarking",
        "leaderboard",
    ],

    "AI Reasoning": [
        "reasoning",
        "reasoning model",
        "reasoning models",
        "logical reasoning",
        "mathematical reasoning",
        "commonsense reasoning",
        "chain of thought",
        "chain-of-thought",
        "planning",
    ],

    "Robotics": [
        "robot",
        "robots",
        "robotics",
        "robotic",
        "embodied ai",
        "embodied intelligence",
        "manipulation",
        "navigation",
        "sim-to-real",
    ],

    "Speech and Audio": [
        "speech recognition",
        "speech synthesis",
        "speech",
        "audio",
        "voice",
        "automatic speech recognition",
        "text-to-speech",
        "acoustic",
    ],

    "Time Series": [
        "time series",
        "time-series",
        "forecasting",
        "temporal",
        "sequence forecasting",
        "time series forecasting",
    ],

    "Graph Machine Learning": [
        "graph neural network",
        "graph neural networks",
        "gnn",
        "graph learning",
        "graph representation",
        "knowledge graph",
        "graph transformer",
    ],

    "Recommender Systems": [
        "recommendation",
        "recommendations",
        "recommender system",
        "recommender systems",
        "personalization",
        "ranking",
        "user preference",
    ],

    "Federated Learning": [
        "federated learning",
        "federated",
        "federated model",
        "federated optimization",
    ],

    "Privacy and Security": [
        "privacy",
        "private",
        "differential privacy",
        "data privacy",
        "cybersecurity",
        "cyber security",
        "attack",
        "attacks",
        "secure",
    ],

    "Scientific AI": [
        "scientific discovery",
        "scientific ai",
        "ai scientist",
        "scientific machine learning",
        "molecular",
        "protein",
        "drug discovery",
        "materials discovery",
        "scientific reasoning",
    ],
}


# =========================================================
# Load dataset
# =========================================================

def load_papers() -> list[dict[str, Any]]:

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
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
# Normalize text
# =========================================================

def normalize_text(
    text: Any
) -> str:

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# Build searchable paper text
# =========================================================

def build_search_text(
    paper: dict[str, Any]
) -> str:

    title = normalize_text(
        paper.get(
            "title",
            ""
        )
    )

    abstract = normalize_text(
        paper.get(
            "abstract",
            ""
        )
    )

    keywords = paper.get(
        "keywords",
        []
    )

    if not isinstance(
        keywords,
        list
    ):

        keywords = []

    keyword_text = " ".join(
        normalize_text(keyword)
        for keyword in keywords
    )

    # Title is repeated to give it higher importance.
    return (
        f"{title} "
        f"{title} "
        f"{keyword_text} "
        f"{abstract}"
    )


# =========================================================
# Check keyword occurrence
# =========================================================

def keyword_matches(
    text: str,
    keyword: str
) -> bool:

    keyword = normalize_text(
        keyword
    )

    if not keyword:
        return False

    # Phrase matching
    if " " in keyword or "-" in keyword:

        return keyword in text

    # Word boundary matching
    pattern = (
        r"\b"
        + re.escape(keyword)
        + r"\b"
    )

    return re.search(
        pattern,
        text
    ) is not None


# =========================================================
# Classify one paper
# =========================================================

def classify_paper(
    paper: dict[str, Any]
) -> tuple[list[str], dict[str, int]]:

    text = build_search_text(
        paper
    )

    topic_scores = {}

    for topic, keywords in (
        TOPIC_KEYWORDS.items()
    ):

        score = 0

        for keyword in keywords:

            if keyword_matches(
                text,
                keyword
            ):

                # Multi-word phrases are stronger signals.
                if " " in keyword:

                    score += 2

                else:

                    score += 1

        if score >= MIN_TOPIC_SCORE:

            topic_scores[
                topic
            ] = score

    # Sort by score
    sorted_topics = sorted(
        topic_scores.items(),
        key=lambda item: (
            -item[1],
            item[0]
        )
    )

    topics = [
        topic
        for topic, score
        in sorted_topics
    ]

    return (
        topics,
        dict(sorted_topics)
    )


# =========================================================
# Add fallback topic
# =========================================================

def ensure_topic(
    topics: list[str]
) -> list[str]:

    if topics:

        return topics

    return [
        "General AI/ML"
    ]


# =========================================================
# Add topic classification
# =========================================================

def classify_all_papers(
    papers: list[dict[str, Any]]
) -> list[dict[str, Any]]:

    classified = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        topics, scores = (
            classify_paper(
                paper
            )
        )

        topics = ensure_topic(
            topics
        )

        enriched = dict(
            paper
        )

        enriched["topics"] = topics

        # Keep scores for transparency.
        enriched[
            "topic_scores"
        ] = scores

        classified.append(
            enriched
        )

        if index % 100 == 0:

            print(
                f"[CLASSIFIED] "
                f"{index} papers"
            )

    return classified


# =========================================================
# Calculate topic statistics
# =========================================================

def calculate_topic_statistics(
    papers: list[dict[str, Any]]
) -> dict[str, int]:

    statistics = {}

    for paper in papers:

        topics = paper.get(
            "topics",
            []
        )

        if not isinstance(
            topics,
            list
        ):
            continue

        for topic in topics:

            statistics[topic] = (
                statistics.get(
                    topic,
                    0
                ) + 1
            )

    return dict(
        sorted(
            statistics.items(),
            key=lambda item: (
                -item[1],
                item[0]
            )
        )
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
        "Day 2 - Step 3: Topic Classification"
    )
    print("=" * 70)

    print(
        "\nLoading keyword-enriched dataset..."
    )

    papers = load_papers()

    print(
        f"Loaded {len(papers)} papers."
    )

    print(
        "\nClassifying research topics..."
    )

    classified_papers = (
        classify_all_papers(
            papers
        )
    )

    print(
        "\nCalculating topic statistics..."
    )

    statistics = (
        calculate_topic_statistics(
            classified_papers
        )
    )

    print(
        "\nResearch topic distribution:"
    )

    for index, (
        topic,
        count
    ) in enumerate(
        statistics.items(),
        start=1
    ):

        print(
            f"{index:2}. "
            f"{topic:<30} "
            f"{count}"
        )

    print(
        "\nSaving topic-enriched dataset..."
    )

    save_dataset(
        classified_papers
    )

    print("\n" + "=" * 70)

    print(
        "DAY 2 - STEP 3 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Total papers : "
        f"{len(classified_papers)}"
    )

    print(
        f"Topics       : "
        f"{len(statistics)}"
    )

    print(
        f"Output       : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()