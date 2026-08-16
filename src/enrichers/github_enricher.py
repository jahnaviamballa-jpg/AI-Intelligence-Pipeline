import asyncio
import os
import random
import re
import ssl
import time
from typing import Optional
from urllib.parse import urlparse

import aiohttp
import certifi
from dotenv import load_dotenv


# =========================================================
# Environment
# =========================================================

load_dotenv()


# =========================================================
# Configuration
# =========================================================

GITHUB_API_URL = "https://api.github.com/repos"

REQUEST_TIMEOUT = 20

MAX_CONCURRENT_REQUESTS = 5

MAX_RETRIES = 3

USER_AGENT = "AI-Intelligence-Pipeline/1.0"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# =========================================================
# Global GitHub rate-limit state
# =========================================================

_rate_limit_lock = asyncio.Lock()

_rate_limit_until: float = 0.0

_rate_limit_active: bool = False

_rate_limit_reset_timestamp: Optional[int] = None


# =========================================================
# In-memory repository cache
# =========================================================

_repository_cache: dict[str, Optional[dict]] = {}


# =========================================================
# SSL
# =========================================================

def create_ssl_context():

    return ssl.create_default_context(
        cafile=certifi.where()
    )


# =========================================================
# Build HTTP headers
# =========================================================

def build_headers():

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if GITHUB_TOKEN:

        headers["Authorization"] = (
            f"Bearer {GITHUB_TOKEN}"
        )

    return headers


# =========================================================
# Extract GitHub repository URL
# =========================================================

def extract_github_url(
    text: str
) -> Optional[str]:

    if not text:
        return None

    pattern = (
        r"https?://(?:www\.)?"
        r"github\.com/"
        r"[A-Za-z0-9_.-]+/"
        r"[A-Za-z0-9_.-]+"
    )

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    for url in matches:

        parsed = urlparse(url)

        parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if len(parts) < 2:
            continue

        owner = parts[0]

        repo = parts[1]

        repo = repo.rstrip(
            ".,;:!?)]}"
        )

        if not owner or not repo:
            continue

        return (
            f"https://github.com/"
            f"{owner}/{repo}"
        )

    return None


# =========================================================
# Get repository key
# =========================================================

def get_repository_key(
    github_url: str
) -> Optional[str]:

    parsed = urlparse(
        str(github_url)
    )

    parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if len(parts) < 2:
        return None

    owner = parts[0].strip()

    repo = parts[1].strip()

    repo = repo.rstrip(
        ".,;:!?)]}"
    )

    if not owner or not repo:
        return None

    return f"{owner}/{repo}"


# =========================================================
# Calculate exponential backoff + jitter
# =========================================================

def calculate_backoff(
    attempt: int
) -> float:

    base_delay = 2 ** (attempt - 1)

    jitter = random.uniform(
        0.2,
        1.0
    )

    return base_delay + jitter


# =========================================================
# Activate global rate limit
# =========================================================

async def activate_global_rate_limit(
    reset_timestamp: Optional[int] = None,
    retry_after: Optional[float] = None,
):

    global _rate_limit_until
    global _rate_limit_active
    global _rate_limit_reset_timestamp

    async with _rate_limit_lock:

        now = time.time()

        if reset_timestamp:

            delay = max(
                0.0,
                reset_timestamp - now
            )

            _rate_limit_reset_timestamp = (
                reset_timestamp
            )

        elif retry_after is not None:

            delay = max(
                0.0,
                retry_after
            )

        else:

            delay = 5.0

        _rate_limit_until = (
            now + delay
        )

        _rate_limit_active = True


# =========================================================
# Check global rate limit
# =========================================================

async def check_global_rate_limit():

    global _rate_limit_active
    global _rate_limit_until

    async with _rate_limit_lock:

        if not _rate_limit_active:
            return True

        now = time.time()

        if now >= _rate_limit_until:

            _rate_limit_active = False

            _rate_limit_until = 0.0

            return True

        remaining = (
            _rate_limit_until - now
        )

        print(
            "[GitHub] Global rate limit active."
        )

        if _rate_limit_reset_timestamp:

            print(
                "Reset timestamp:",
                _rate_limit_reset_timestamp
            )

        print(
            f"Cooldown remaining: "
            f"{remaining:.1f}s"
        )

        return False


# =========================================================
# Parse Retry-After
# =========================================================

def parse_retry_after(
    value: Optional[str]
) -> Optional[float]:

    if not value:
        return None

    try:

        return float(value)

    except ValueError:

        return None


# =========================================================
# Parse GitHub reset timestamp
# =========================================================

def parse_reset_timestamp(
    value: Optional[str]
) -> Optional[int]:

    if not value:
        return None

    try:

        return int(value)

    except ValueError:

        return None


# =========================================================
# Fetch normal URL
# =========================================================

async def fetch_url(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
):

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        delay = 0

        try:

            async with semaphore:

                async with session.get(
                    str(url)
                ) as response:

                    # -------------------------------------
                    # Too many requests
                    # -------------------------------------

                    if response.status == 429:

                        retry_after = (
                            parse_retry_after(
                                response.headers.get(
                                    "Retry-After"
                                )
                            )
                        )

                        delay = (
                            retry_after
                            if retry_after is not None
                            else calculate_backoff(
                                attempt
                            )
                        )

                        print(
                            f"[429] {url} "
                            f"→ retrying in "
                            f"{delay:.1f}s"
                        )

                    # -------------------------------------
                    # Server error
                    # -------------------------------------

                    elif response.status >= 500:

                        delay = (
                            calculate_backoff(
                                attempt
                            )
                        )

                        print(
                            f"[{response.status}] "
                            f"{url} "
                            f"→ retrying in "
                            f"{delay:.1f}s"
                        )

                    # -------------------------------------
                    # Other error
                    # -------------------------------------

                    elif response.status != 200:

                        return None

                    # -------------------------------------
                    # Success
                    # -------------------------------------

                    else:

                        return await response.text()

            if delay > 0:

                await asyncio.sleep(
                    delay
                )

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ) as error:

            if attempt == MAX_RETRIES:

                print(
                    f"[FAILED] {url}: "
                    f"{error}"
                )

                return None

            delay = calculate_backoff(
                attempt
            )

            print(
                f"[RETRY {attempt}] "
                f"{url} "
                f"→ waiting "
                f"{delay:.1f}s"
            )

            await asyncio.sleep(
                delay
            )

    return None


# =========================================================
# Find GitHub repository from arXiv paper page
# =========================================================

async def find_github_from_paper_page(
    session: aiohttp.ClientSession,
    paper_url: str,
    semaphore: asyncio.Semaphore,
):

    html = await fetch_url(
        session,
        str(paper_url),
        semaphore,
    )

    if not html:
        return None

    return extract_github_url(
        html
    )


# =========================================================
# Fetch GitHub repository metadata
# =========================================================

async def fetch_github_repository(
    session: aiohttp.ClientSession,
    github_url: str,
    semaphore: asyncio.Semaphore,
):

    github_url = str(
        github_url
    )

    repository_key = (
        get_repository_key(
            github_url
        )
    )

    if not repository_key:
        return None

    # -----------------------------------------------------
    # Cache lookup
    # -----------------------------------------------------

    if repository_key in _repository_cache:

        return _repository_cache[
            repository_key
        ]

    # -----------------------------------------------------
    # Global rate-limit check
    # -----------------------------------------------------

    if not await check_global_rate_limit():

        _repository_cache[
            repository_key
        ] = None

        return None

    api_url = (
        f"{GITHUB_API_URL}/"
        f"{repository_key}"
    )

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        if not await check_global_rate_limit():

            _repository_cache[
                repository_key
            ] = None

            return None

        delay = 0

        try:

            async with semaphore:

                async with session.get(
                    api_url
                ) as response:

                    # =====================================
                    # SUCCESS
                    # =====================================

                    if response.status == 200:

                        data = (
                            await response.json()
                        )

                        result = {
                            "github_url": data.get(
                                "html_url"
                            ),
                            "github_stars": data.get(
                                "stargazers_count"
                            ),
                        }

                        _repository_cache[
                            repository_key
                        ] = result

                        return result

                    # =====================================
                    # NOT FOUND
                    # =====================================

                    if response.status == 404:

                        print(
                            f"[GitHub 404] "
                            f"{github_url}"
                        )

                        _repository_cache[
                            repository_key
                        ] = None

                        return None

                    # =====================================
                    # TOO MANY REQUESTS
                    # =====================================

                    if response.status == 429:

                        retry_after = (
                            parse_retry_after(
                                response.headers.get(
                                    "Retry-After"
                                )
                            )
                        )

                        reset_timestamp = (
                            parse_reset_timestamp(
                                response.headers.get(
                                    "X-RateLimit-Reset"
                                )
                            )
                        )

                        print(
                            f"[GitHub 429] "
                            f"{github_url}"
                        )

                        await activate_global_rate_limit(
                            reset_timestamp=(
                                reset_timestamp
                            ),
                            retry_after=(
                                retry_after
                            ),
                        )

                        return None

                    # =====================================
                    # FORBIDDEN / RATE LIMIT
                    # =====================================

                    if response.status == 403:

                        remaining = (
                            response.headers.get(
                                "X-RateLimit-Remaining"
                            )
                        )

                        reset_timestamp = (
                            parse_reset_timestamp(
                                response.headers.get(
                                    "X-RateLimit-Reset"
                                )
                            )
                        )

                        if remaining == "0":

                            print(
                                "[GitHub] "
                                "API rate limit reached."
                            )

                            if reset_timestamp:

                                print(
                                    "Reset timestamp:",
                                    reset_timestamp
                                )

                            await activate_global_rate_limit(
                                reset_timestamp=(
                                    reset_timestamp
                                )
                            )

                            return None

                        print(
                            f"[GitHub 403] "
                            f"{github_url}"
                        )

                        return None

                    # =====================================
                    # SERVER ERROR
                    # =====================================

                    if response.status >= 500:

                        delay = (
                            calculate_backoff(
                                attempt
                            )
                        )

                        print(
                            f"[GitHub "
                            f"{response.status}] "
                            f"{github_url} "
                            f"→ retrying in "
                            f"{delay:.1f}s"
                        )

                    else:

                        print(
                            f"[GitHub "
                            f"{response.status}] "
                            f"{github_url}"
                        )

                        return None

            if delay > 0:

                await asyncio.sleep(
                    delay
                )

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ) as error:

            if attempt == MAX_RETRIES:

                print(
                    f"[GitHub FAILED] "
                    f"{github_url}: "
                    f"{error}"
                )

                return None

            delay = calculate_backoff(
                attempt
            )

            print(
                f"[GitHub RETRY {attempt}] "
                f"{github_url} "
                f"→ waiting "
                f"{delay:.1f}s"
            )

            await asyncio.sleep(
                delay
            )

    return None


# =========================================================
# Enrich one paper
# =========================================================

async def enrich_paper(
    session: aiohttp.ClientSession,
    paper: dict,
    semaphore: asyncio.Semaphore,
):

    paper["github_url"] = None

    paper["github_stars"] = None

    # -----------------------------------------------------
    # Check existing metadata
    # -----------------------------------------------------

    source_text = " ".join(
        [
            str(
                paper.get(
                    "summary",
                    ""
                )
            ),
            str(
                paper.get(
                    "links_text",
                    ""
                )
            ),
        ]
    )

    github_url = extract_github_url(
        source_text
    )

    # -----------------------------------------------------
    # Search arXiv paper page
    # -----------------------------------------------------

    if not github_url:

        github_url = (
            await find_github_from_paper_page(
                session,
                str(
                    paper["paper_url"]
                ),
                semaphore,
            )
        )

    # -----------------------------------------------------
    # No repository found
    # -----------------------------------------------------

    if not github_url:

        return paper

    # -----------------------------------------------------
    # Verify repository
    # -----------------------------------------------------

    github_data = (
        await fetch_github_repository(
            session,
            github_url,
            semaphore,
        )
    )

    if github_data:

        paper["github_url"] = (
            github_data["github_url"]
        )

        paper["github_stars"] = (
            github_data["github_stars"]
        )

    return paper


# =========================================================
# Enrich all papers concurrently
# =========================================================

async def enrich_papers(
    papers: list[dict],
):

    ssl_context = (
        create_ssl_context()
    )

    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=MAX_CONCURRENT_REQUESTS,
    )

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    headers = build_headers()

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_REQUESTS
    )

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=headers,
    ) as session:

        tasks = [
            enrich_paper(
                session,
                paper,
                semaphore,
            )
            for paper in papers
        ]

        enriched_papers = (
            await asyncio.gather(
                *tasks
            )
        )

    return enriched_papers