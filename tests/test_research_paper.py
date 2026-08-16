from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models.research_paper import ResearchPaper


def test_valid_research_paper():
    paper = ResearchPaper(
        title="Artificial Intelligence Research",
        authors=["Alice", "Bob"],
        paper_url="https://arxiv.org/abs/1234.5678",
        github_url="https://github.com/example/research",
        github_stars=100,
        published_date=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert paper.title == "Artificial Intelligence Research"
    assert paper.authors == ["Alice", "Bob"]
    assert str(paper.paper_url) == (
        "https://arxiv.org/abs/1234.5678"
    )
    assert str(paper.github_url) == (
        "https://github.com/example/research"
    )
    assert paper.github_stars == 100


def test_github_information_is_optional():
    paper = ResearchPaper(
        title="AI Paper",
        authors=["Alice"],
        paper_url="https://arxiv.org/abs/1234.5678",
        published_date=None,
    )

    assert paper.github_url is None
    assert paper.github_stars is None
    assert paper.published_date is None


def test_empty_title_is_rejected():
    with pytest.raises(ValidationError):
        ResearchPaper(
            title="",
            authors=["Alice"],
            paper_url="https://arxiv.org/abs/1234.5678",
            published_date=None,
        )


def test_negative_github_stars_are_rejected():
    with pytest.raises(ValidationError):
        ResearchPaper(
            title="AI Paper",
            authors=["Alice"],
            paper_url="https://arxiv.org/abs/1234.5678",
            github_stars=-1,
            published_date=None,
        )


def test_invalid_paper_url_is_rejected():
    with pytest.raises(ValidationError):
        ResearchPaper(
            title="AI Paper",
            authors=["Alice"],
            paper_url="not-a-valid-url",
            published_date=None,
        )


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        ResearchPaper(
            title="AI Paper",
            authors=["Alice"],
            paper_url="https://arxiv.org/abs/1234.5678",
            published_date=None,
            unexpected_field="not allowed",
        )


def test_default_schema_values():
    paper = ResearchPaper(
        title="AI Paper",
        authors=["Alice"],
        paper_url="https://arxiv.org/abs/1234.5678",
        published_date=None,
    )

    assert paper.schemaVersion == "1.0"
    assert paper.recordType == "RESEARCH_PAPER"


def test_json_serialization():
    paper = ResearchPaper(
        title="AI Paper",
        authors=["Alice"],
        paper_url="https://arxiv.org/abs/1234.5678",
        github_url="https://github.com/example/research",
        github_stars=50,
        published_date=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    data = paper.model_dump(mode="json")

    assert data["title"] == "AI Paper"
    assert data["github_stars"] == 50
    assert data["schemaVersion"] == "1.0"
    assert data["recordType"] == "RESEARCH_PAPER"