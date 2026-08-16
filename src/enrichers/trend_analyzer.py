import json
import re
from collections import Counter
from pathlib import Path


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = Path(
    "data/processed/research_intelligence_papers.json"
)

OUTPUT_FILE = Path(
    "data/processed/trend_enriched_papers.json"
)

PROGRESS_INTERVAL = 100


# =========================================================
# Trend vocabulary
# =========================================================

TREND_GROUPS = {

    "Agentic AI": {
        "agents",
        "agent",
        "agentic",
        "multi-agent",
        "multiagent",
        "autonomous",
        "tool use",
        "tool-use",
        "planning",
        "workflow",
    },

    "Large Language Models": {
        "llm",
        "llms",
        "language model",
        "language models",
        "large language",
        "transformer",
        "instruction tuning",
        "instruction-tuning",
        "fine-tuning",
        "finetuning",
    },

    "Generative AI": {
        "generation",
        "generative",
        "diffusion",
        "text generation",
        "image generation",
        "video generation",
        "synthetic data",
    },

    "AI Reasoning": {
        "reasoning",
        "chain of thought",
        "chain-of-thought",
        "planning",
        "inference",
        "logical reasoning",
        "mathematical reasoning",
    },

    "AI Evaluation": {
        "evaluation",
        "benchmark",
        "benchmarks",
        "eval",
        "metrics",
        "assessment",
        "testing",
    },

    "AI Safety": {
        "safety",
        "alignment",
        "robustness",
        "risk",
        "trustworthy",
        "reliable",
        "guardrail",
        "guardrails",
    },

    "Multimodal AI": {
        "multimodal",
        "multi-modal",
        "vision-language",
        "vision language",
        "audio-visual",
        "image-text",
        "video-language",
    },

    "Computer Vision": {
        "computer vision",
        "image",
        "images",
        "visual",
        "object detection",
        "segmentation",
        "tracking",
        "video",
    },

    "Natural Language Processing": {
        "nlp",
        "natural language",
        "text",
        "language",
        "translation",
        "sentiment",
        "question answering",
        "information extraction",
    },

    "Reinforcement Learning": {
        "reinforcement learning",
        "rl",
        "policy",
        "reward",
        "agent",
        "environment",
        "offline reinforcement",
    },

    "Robotics": {
        "robot",
        "robotics",
        "manipulation",
        "navigation",
        "embodied",
        "embodied ai",
    },

    "Privacy and Security": {
        "privacy",
        "security",
        "attack",
        "adversarial",
        "defense",
        "secure",
        "spoofing",
        "cybersecurity",
    },

    "Scientific AI": {
        "scientific",
        "science",
        "biology",
        "chemistry",
        "physics",
        "medical",
        "drug discovery",
        "molecular",
    },

    "Optimization": {
        "optimization",
        "optimisation",
        "optimizer",
        "optimizers",
        "gradient",
        "search",
        "efficient",
    },

    "Time Series": {
        "time series",
        "forecasting",
        "temporal",
        "time-series",
        "prediction",
    },
}


# =========================================================
# Research stage vocabulary
# =========================================================

EMERGING_TERMS = {
    "agentic",
    "multimodal",
    "reasoning",
    "generative",
    "diffusion",
    "foundation model",
    "large language",
    "llm",
    "autonomous",
    "embodied ai",
}

MATURE_TERMS = {
    "classification",
    "regression",
    "traditional machine learning",
    "random forest",
    "svm",
    "support vector",
    "cnn",
    "convolutional neural network",
}


# =========================================================
# Application vocabulary
# =========================================================

APPLICATION_GROUPS = {

    "Healthcare": {
        "medical",
        "healthcare",
        "clinical",
        "disease",
        "patient",
        "diagnosis",
        "medicine",
        "drug",
    },

    "Education": {
        "education",
        "student",
        "learning",
        "teaching",
        "tutor",
        "classroom",
        "pedagogical",
    },

    "Finance": {
        "finance",
        "financial",
        "stock",
        "trading",
        "banking",
        "credit",
        "fraud",
    },

    "Security": {
        "security",
        "cybersecurity",
        "attack",
        "malware",
        "privacy",
        "adversarial",
    },

    "Robotics": {
        "robot",
        "robotics",
        "navigation",
        "manipulation",
        "embodied",
    },

    "Software Engineering": {
        "software",
        "code",
        "coding",
        "programming",
        "repository",
        "developer",
        "software engineering",
    },

    "Science": {
        "scientific",
        "biology",
        "chemistry",
        "physics",
        "molecular",
        "astronomy",
    },
}


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
# Build paper text
# =========================================================

def build_paper_text(paper):

    title = normalize_text(
        paper.get("title", "")
    )

    summary = normalize_text(
        paper.get("summary", "")
    )

    keywords = normalize_text(
        paper.get("keywords", [])
    )

    topic = normalize_text(
        paper.get("topic", "")
    )

    return " ".join(
        [
            title,
            summary,
            keywords,
            topic,
        ]
    )


# =========================================================
# Count matching terms
# =========================================================

def count_group_matches(
    text,
    vocabulary
):

    matches = []

    for term in vocabulary:

        normalized_term = normalize_text(
            term
        )

        if not normalized_term:
            continue

        if normalized_term in text:
            matches.append(
                term
            )

    return matches


# =========================================================
# Detect research trends
# =========================================================

def detect_trends(paper):

    text = build_paper_text(
        paper
    )

    detected = []

    trend_scores = {}

    for group_name, vocabulary in (
        TREND_GROUPS.items()
    ):

        matches = count_group_matches(
            text,
            vocabulary
        )

        if matches:

            detected.append(
                group_name
            )

            trend_scores[
                group_name
            ] = len(matches)

    # Sort strongest trends first
    detected.sort(
        key=lambda name:
        trend_scores[name],
        reverse=True
    )

    return detected, trend_scores


# =========================================================
# Determine primary research area
# =========================================================

def determine_research_area(
    paper,
    detected_trends
):

    topic = paper.get(
        "topic"
    )

    if topic:
        topic = str(
            topic
        ).strip()

        if topic:
            return topic

    if detected_trends:
        return detected_trends[0]

    return "General AI/ML"


# =========================================================
# Determine research stage
# =========================================================

def determine_research_stage(
    paper
):

    text = build_paper_text(
        paper
    )

    emerging_score = 0
    mature_score = 0

    for term in EMERGING_TERMS:

        if normalize_text(term) in text:
            emerging_score += 1

    for term in MATURE_TERMS:

        if normalize_text(term) in text:
            mature_score += 1

    if emerging_score >= 2:
        return "Emerging"

    if mature_score >= 2:
        return "Mature"

    return "Developing"


# =========================================================
# Detect applications
# =========================================================

def detect_applications(
    paper
):

    text = build_paper_text(
        paper
    )

    applications = []

    application_scores = {}

    for group_name, vocabulary in (
        APPLICATION_GROUPS.items()
    ):

        matches = count_group_matches(
            text,
            vocabulary
        )

        if matches:

            applications.append(
                group_name
            )

            application_scores[
                group_name
            ] = len(matches)

    applications.sort(
        key=lambda name:
        application_scores[name],
        reverse=True
    )

    return applications


# =========================================================
# Generate trend signals
# =========================================================

def generate_trend_signals(
    detected_trends
):

    signals = []

    for trend in detected_trends:

        if trend == "Agentic AI":
            signals.append(
                "agentic AI"
            )

        elif trend == "Large Language Models":
            signals.append(
                "LLM research"
            )

        elif trend == "Generative AI":
            signals.append(
                "generative AI"
            )

        elif trend == "AI Reasoning":
            signals.append(
                "AI reasoning"
            )

        elif trend == "AI Evaluation":
            signals.append(
                "AI evaluation"
            )

        elif trend == "AI Safety":
            signals.append(
                "AI safety"
            )

        elif trend == "Multimodal AI":
            signals.append(
                "multimodal AI"
            )

        else:
            signals.append(
                trend.lower()
            )

    return signals


# =========================================================
# Generate technical signals
# =========================================================

def generate_technical_signals(
    paper
):

    text = build_paper_text(
        paper
    )

    technical_terms = [
        "transformer",
        "attention",
        "fine-tuning",
        "reinforcement learning",
        "diffusion",
        "retrieval augmented generation",
        "rag",
        "benchmark",
        "optimization",
        "classification",
        "generation",
        "reasoning",
        "embedding",
        "representation",
        "neural network",
        "language model",
        "multimodal",
        "agent",
    ]

    found = []

    for term in technical_terms:

        if normalize_text(term) in text:

            found.append(
                term
            )

    return found


# =========================================================
# Generate application signals
# =========================================================

def generate_application_signals(
    applications
):

    return [
        application.lower()
        for application in applications
    ]


# =========================================================
# Enrich one paper
# =========================================================

def enrich_paper(paper):

    detected_trends, trend_scores = (
        detect_trends(
            paper
        )
    )

    research_area = (
        determine_research_area(
            paper,
            detected_trends
        )
    )

    research_stage = (
        determine_research_stage(
            paper
        )
    )

    applications = (
        detect_applications(
            paper
        )
    )

    trend_signals = (
        generate_trend_signals(
            detected_trends
        )
    )

    technical_signals = (
        generate_technical_signals(
            paper
        )
    )

    application_signals = (
        generate_application_signals(
            applications
        )
    )

    paper["research_area"] = (
        research_area
    )

    paper["research_stage"] = (
        research_stage
    )

    paper["detected_trends"] = (
        detected_trends
    )

    paper["trend_scores"] = (
        trend_scores
    )

    paper["trend_signals"] = (
        trend_signals
    )

    paper["technical_signals"] = (
        technical_signals
    )

    paper["application_areas"] = (
        applications
    )

    paper["application_signals"] = (
        application_signals
    )

    return paper


# =========================================================
# Enrich all papers
# =========================================================

def enrich_papers(papers):

    print(
        "\nAnalyzing research trends..."
    )

    enriched = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        enriched_paper = (
            enrich_paper(
                paper
            )
        )

        enriched.append(
            enriched_paper
        )

        if (
            index % PROGRESS_INTERVAL
            == 0
        ):

            print(
                f"[TRENDS] "
                f"{index} papers analyzed"
            )

    return enriched


# =========================================================
# Calculate statistics
# =========================================================

def calculate_statistics(
    papers
):

    trend_counter = Counter()

    stage_counter = Counter()

    application_counter = Counter()

    area_counter = Counter()

    for paper in papers:

        for trend in paper.get(
            "detected_trends",
            []
        ):

            trend_counter[
                trend
            ] += 1

        stage = paper.get(
            "research_stage"
        )

        if stage:
            stage_counter[
                stage
            ] += 1

        for application in paper.get(
            "application_areas",
            []
        ):

            application_counter[
                application
            ] += 1

        area = paper.get(
            "research_area"
        )

        if area:
            area_counter[
                area
            ] += 1

    return (
        trend_counter,
        stage_counter,
        application_counter,
        area_counter,
    )

# =========================================================
# Load dataset
# =========================================================

def load_dataset():

    print(
        "\nLoading research intelligence dataset..."
    )

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
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
        "\nSaving trend-enriched dataset..."
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
        "Day 2 - Step 6: Research Trend Analysis"
    )

    print("=" * 70)

    papers = load_dataset()

    enriched_papers = enrich_papers(
        papers
    )

    (
        trend_counter,
        stage_counter,
        application_counter,
        area_counter,
    ) = calculate_statistics(
        enriched_papers
    )

    print(
        "\nTop research trends:"
    )

    for index, (
        trend,
        count
    ) in enumerate(
        trend_counter.most_common(15),
        start=1
    ):

        print(
            f"{index:2}. "
            f"{trend:<30} "
            f"{count}"
        )

    print(
        "\nResearch stage distribution:"
    )

    for stage, count in (
        stage_counter.most_common()
    ):

        print(
            f"{stage:<15} "
            f"{count}"
        )

    print(
        "\nTop application areas:"
    )

    for index, (
        application,
        count
    ) in enumerate(
        application_counter.most_common(10),
        start=1
    ):

        print(
            f"{index:2}. "
            f"{application:<25} "
            f"{count}"
        )

    print(
        "\nTop research areas:"
    )

    for index, (
        area,
        count
    ) in enumerate(
        area_counter.most_common(10),
        start=1
    ):

        print(
            f"{index:2}. "
            f"{area:<30} "
            f"{count}"
        )

    save_dataset(
        enriched_papers
    )

    print("\n" + "=" * 70)

    print(
        "DAY 2 - STEP 6 COMPLETED"
    )

    print("=" * 70)

    print(
        f"Total papers : "
        f"{len(enriched_papers)}"
    )

    print(
        f"Trend groups : "
        f"{len(TREND_GROUPS)}"
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