import pytest

from src.crawlers.arxiv_crawler import (
    parse_arxiv_response,
    deduplicate_papers,
)


def test_parse_arxiv_response():
    xml_data = """
    <?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <id>http://arxiv.org/abs/2601.12345</id>

            <title>
                A Test Paper About Artificial Intelligence
            </title>

            <summary>
                This is a test research paper.
            </summary>

            <published>
                2026-01-15T12:00:00Z
            </published>

            <author>
                <name>Alice</name>
            </author>

            <author>
                <name>Bob</name>
            </author>

            <link
                href="http://arxiv.org/abs/2601.12345"
                rel="alternate"
                type="text/html"
            />
        </entry>
    </feed>
    """

    papers = parse_arxiv_response(xml_data)

    assert len(papers) == 1

    paper = papers[0]

    assert paper["arxiv_id"] == "2601.12345"

    assert (
        paper["title"]
        == "A Test Paper About Artificial Intelligence"
    )

    assert paper["authors"] == [
        "Alice",
        "Bob",
    ]

    assert (
        paper["paper_url"]
        == "http://arxiv.org/abs/2601.12345"
    )

    assert (
        paper["summary"]
        == "This is a test research paper."
    )

    assert paper["published_date"] is not None

    assert paper["github_url"] is None

    assert paper["github_stars"] is None


def test_parse_arxiv_response_handles_empty_feed():

    xml_data = """
    <?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
    </feed>
    """

    papers = parse_arxiv_response(xml_data)

    assert papers == []


def test_deduplicate_papers():

    papers = [
        {
            "arxiv_id": "2601.12345",
            "title": "Paper One",
        },
        {
            "arxiv_id": "2601.12345",
            "title": "Paper One Duplicate",
        },
        {
            "arxiv_id": "2601.67890",
            "title": "Paper Two",
        },
    ]

    unique = deduplicate_papers(papers)

    assert len(unique) == 2

    assert unique[0]["arxiv_id"] == "2601.12345"

    assert unique[1]["arxiv_id"] == "2601.67890"


def test_deduplicate_papers_removes_missing_ids():

    papers = [
        {
            "arxiv_id": None,
            "title": "Invalid Paper",
        },
        {
            "arxiv_id": "",
            "title": "Another Invalid Paper",
        },
        {
            "arxiv_id": "2601.12345",
            "title": "Valid Paper",
        },
    ]

    unique = deduplicate_papers(papers)

    assert len(unique) == 1

    assert unique[0]["arxiv_id"] == "2601.12345"