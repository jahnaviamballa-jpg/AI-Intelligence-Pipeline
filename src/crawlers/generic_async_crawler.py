import ssl
import certifi
import asyncio
from typing import Iterable

import aiohttp
from bs4 import BeautifulSoup


class AsyncCrawler:
    """
    Reusable asynchronous HTTP crawler.

    Features:
    - Concurrent requests
    - Connection pooling
    - Request timeout
    - Retry with exponential backoff
    - Retry handling for 429 and 5xx responses
    - HTML parsing
    """

    def __init__(
        self,
        concurrency: int = 10,
        timeout: int = 20,
        max_retries: int = 3,
    ):
        self.concurrency = concurrency
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch(
        self,
        session: aiohttp.ClientSession,
        url: str,
    ) -> dict:

        for attempt in range(self.max_retries + 1):

            try:
                async with session.get(url) as response:

                    if response.status == 200:
                        html = await response.text()

                        return {
                            "url": url,
                            "status": response.status,
                            "html": html,
                        }

                    if response.status == 429 or response.status >= 500:

                        if attempt < self.max_retries:
                            delay = (2 ** attempt) + 0.5
                            await asyncio.sleep(delay)
                            continue

                    return {
                        "url": url,
                        "status": response.status,
                        "html": "",
                    }

            except (aiohttp.ClientError, asyncio.TimeoutError):

                if attempt < self.max_retries:
                    delay = (2 ** attempt) + 0.5
                    await asyncio.sleep(delay)
                    continue

                return {
                    "url": url,
                    "status": 0,
                    "html": "",
                }

        return {
            "url": url,
            "status": 0,
            "html": "",
        }

    async def crawl(
        self,
        urls: Iterable[str],
    ) -> list[dict]:

        timeout = aiohttp.ClientTimeout(
            total=self.timeout
        )

        ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )

        connector = aiohttp.TCPConnector(
            limit=self.concurrency,
            ssl=ssl_context,
        )

        headers = {
            "User-Agent": (
                "AI-Intelligence-Pipeline/1.0 "
                "(research-data-ingestion)"
            )
        }

        semaphore = asyncio.Semaphore(
            self.concurrency
        )

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
        ) as session:

            async def limited_fetch(url: str):

                async with semaphore:
                    return await self.fetch(
                        session,
                        url,
                    )

            tasks = [
                limited_fetch(url)
                for url in urls
            ]

            return await asyncio.gather(
                *tasks
            )


def extract_text(html: str) -> str:
    """Extract readable text from an HTML document."""

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    for element in soup(
        ["script", "style", "noscript"]
    ):
        element.decompose()

    return " ".join(
        soup.stripped_strings
    )


async def main():

    crawler = AsyncCrawler(
        concurrency=5
    )

    results = await crawler.crawl(
        [
            "https://arxiv.org/",
            "https://www.python.org/",
            "https://www.wikipedia.org/",
        ]
    )

    for result in results:

        print(
            result["status"],
            result["url"],
        )

        text = extract_text(
            result["html"]
        )

        print(
            f"Extracted characters: {len(text)}"
        )


if __name__ == "__main__":
    asyncio.run(main())