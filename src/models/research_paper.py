from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ResearchPaper(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    schemaVersion: str = "1.0"
    recordType: str = "RESEARCH_PAPER"

    title: str = Field(
        min_length=1
    )

    authors: list[str]

    paper_url: HttpUrl

    github_url: HttpUrl | None = None

    github_stars: int | None = Field(
        default=None,
        ge=0
    )

    published_date: datetime