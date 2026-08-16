import json
from pathlib import Path

from src.models.research_paper import ResearchPaper


OUTPUT_FILE = Path(
    "data/processed/research_papers.json"
)


def save_research_papers(
    papers: list[ResearchPaper]
):
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [
        paper.model_dump(mode="json")
        for paper in papers
    ]

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

    print(
        f"Saved {len(data)} papers to "
        f"{OUTPUT_FILE}"
    )