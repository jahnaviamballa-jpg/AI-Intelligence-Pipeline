import asyncio

import aiohttp

from src.enrichers import github_enricher


class FakeResponse:

    def __init__(
        self,
        status,
        data=None,
        headers=None,
    ):
        self.status = status
        self._data = data or {}
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    async def json(self):
        return self._data

    async def text(self):
        return ""


class FakeSession:

    def __init__(self, response):
        self.response = response
        self.request_count = 0

    def get(self, url):

        self.request_count += 1

        return self.response


def reset_cache():

    github_enricher._repository_cache.clear()

    github_enricher._rate_limit_active = False

    github_enricher._rate_limit_until = 0.0

    github_enricher._rate_limit_reset_timestamp = None


def test_fetch_github_repository_success():

    reset_cache()

    response = FakeResponse(
        status=200,
        data={
            "html_url": (
                "https://github.com/"
                "test-user/test-repo"
            ),
            "stargazers_count": 42,
        },
    )

    session = FakeSession(response)

    semaphore = asyncio.Semaphore(1)

    result = asyncio.run(
        github_enricher.fetch_github_repository(
            session,
            "https://github.com/test-user/test-repo",
            semaphore,
        )
    )

    assert result == {
        "github_url": (
            "https://github.com/"
            "test-user/test-repo"
        ),
        "github_stars": 42,
    }

    assert session.request_count == 1


def test_fetch_github_repository_not_found():

    reset_cache()

    response = FakeResponse(
        status=404
    )

    session = FakeSession(response)

    semaphore = asyncio.Semaphore(1)

    result = asyncio.run(
        github_enricher.fetch_github_repository(
            session,
            "https://github.com/"
            "test-user/nonexistent-repo",
            semaphore,
        )
    )

    assert result is None

    assert session.request_count == 1


def test_fetch_github_repository_uses_cache():

    reset_cache()

    response = FakeResponse(
        status=200,
        data={
            "html_url": (
                "https://github.com/"
                "test-user/cached-repo"
            ),
            "stargazers_count": 100,
        },
    )

    session = FakeSession(response)

    semaphore = asyncio.Semaphore(1)

    url = (
        "https://github.com/"
        "test-user/cached-repo"
    )

    first_result = asyncio.run(
        github_enricher.fetch_github_repository(
            session,
            url,
            semaphore,
        )
    )

    second_result = asyncio.run(
        github_enricher.fetch_github_repository(
            session,
            url,
            semaphore,
        )
    )

    assert first_result == second_result

    assert session.request_count == 1


def test_fetch_github_repository_zero_stars():

    reset_cache()

    response = FakeResponse(
        status=200,
        data={
            "html_url": (
                "https://github.com/"
                "test-user/new-repo"
            ),
            "stargazers_count": 0,
        },
    )

    session = FakeSession(response)

    semaphore = asyncio.Semaphore(1)

    result = asyncio.run(
        github_enricher.fetch_github_repository(
            session,
            "https://github.com/test-user/new-repo",
            semaphore,
        )
    )

    assert result["github_stars"] == 0


def test_fetch_github_repository_invalid_url():

    reset_cache()

    response = FakeResponse(
        status=200,
        data={
            "html_url": "unused",
            "stargazers_count": 10,
        },
    )

    session = FakeSession(response)

    semaphore = asyncio.Semaphore(1)

    result = asyncio.run(
        github_enricher.fetch_github_repository(
            session,
            "https://github.com/test-user",
            semaphore,
        )
    )

    assert result is None

    assert session.request_count == 0