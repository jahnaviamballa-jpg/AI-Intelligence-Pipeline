import json
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError


# =========================================================
# Configuration
# =========================================================

DATASET_FILE = Path(
    "data/processed/recommended_research_papers.json"
)

SIMILARITY_FILE = Path(
    "data/processed/similarity_index.json"
)

API_METADATA_FILE = Path(
    "data/processed/research_api_metadata.json"
)

API_BASE_URL = "http://127.0.0.1:8000"


# =========================================================
# Helpers
# =========================================================

def load_json(path):

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def check(condition, message):

    if condition:

        print(
            f"[PASS] {message}"
        )

        return True

    print(
        f"[FAIL] {message}"
    )

    return False


def request_json(endpoint):

    url = (
        API_BASE_URL
        + endpoint
    )

    try:

        with urlopen(
            url,
            timeout=10
        ) as response:

            status = response.status

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

            return status, data

    except Exception as error:

        print(
            f"[ERROR] {endpoint}: {error}"
        )

        return None, None


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 70)

    print(
        "AI Intelligence Pipeline"
    )

    print(
        "Day 3 - Step 7: API Server Validator"
    )

    print("=" * 70)

    passed = True

    # -----------------------------------------------------
    # Dataset validation
    # -----------------------------------------------------

    print(
        "\nValidating backend datasets..."
    )

    if not DATASET_FILE.exists():

        print(
            f"[FAIL] Dataset missing: "
            f"{DATASET_FILE}"
        )

        passed = False

    else:

        papers = load_json(
            DATASET_FILE
        )

        passed &= check(
            isinstance(
                papers,
                list
            ),
            "Research dataset is valid."
        )

        passed &= check(
            len(papers) >= 1000,
            "At least 1000 papers available."
        )

    # -----------------------------------------------------
    # Similarity index
    # -----------------------------------------------------

    if not SIMILARITY_FILE.exists():

        print(
            f"[FAIL] Similarity index missing: "
            f"{SIMILARITY_FILE}"
        )

        passed = False

    else:

        similarity = load_json(
            SIMILARITY_FILE
        )

        passed &= check(
            isinstance(
                similarity,
                dict
            ),
            "Similarity index is valid."
        )

    # -----------------------------------------------------
    # API metadata
    # -----------------------------------------------------

    if not API_METADATA_FILE.exists():

        print(
            f"[FAIL] API metadata missing: "
            f"{API_METADATA_FILE}"
        )

        passed = False

    else:

        metadata = load_json(
            API_METADATA_FILE
        )

        passed &= check(
            isinstance(
                metadata,
                dict
            ),
            "API metadata is valid."
        )

    # -----------------------------------------------------
    # API endpoint tests
    # -----------------------------------------------------

    print(
        "\nTesting live API endpoints..."
    )

    endpoints = [
        (
            "/",
            "API root"
        ),
        (
            "/health",
            "Health endpoint"
        ),
        (
            "/papers?limit=5",
            "Papers endpoint"
        ),
        (
            "/search?q=LLM%20reasoning",
            "Search endpoint"
        ),
        (
            "/areas",
            "Research areas endpoint"
        ),
        (
            "/area/Agentic%20AI",
            "Research area filter"
        ),
        (
            "/emerging",
            "Emerging research endpoint"
        ),
        (
            "/recommendations",
            "Recommendations endpoint"
        ),
    ]

    for endpoint, description in endpoints:

        status, data = request_json(
            endpoint
        )

        endpoint_passed = (
            status == 200
            and data is not None
        )

        passed &= check(
            endpoint_passed,
            f"{description}: HTTP {status}"
            if status
            else f"{description}: request failed"
        )

    # -----------------------------------------------------
    # Health response
    # -----------------------------------------------------

    status, health = request_json(
        "/health"
    )

    if status == 200 and health:

        passed &= check(
            health.get(
                "status"
            ) == "healthy",
            "API health status is healthy."
        )

        passed &= check(
            health.get(
                "papers"
            ) >= 1000,
            "API reports at least 1000 papers."
        )

    # -----------------------------------------------------
    # Search response
    # -----------------------------------------------------

    status, search_result = request_json(
        "/search?q=LLM%20reasoning"
    )

    if status == 200 and search_result:

        passed &= check(
            "results" in search_result,
            "Search response contains results."
        )

        passed &= check(
            search_result.get(
                "count",
                0
            ) > 0,
            "Search returns matching papers."
        )

    # -----------------------------------------------------
    # Recommendations response
    # -----------------------------------------------------

    status, recommendation_result = (
        request_json(
            "/recommendations"
        )
    )

    if (
        status == 200
        and recommendation_result
    ):

        passed &= check(
            "papers"
            in recommendation_result,
            "Recommendation response contains papers."
        )

        passed &= check(
            recommendation_result.get(
                "count",
                0
            ) > 0,
            "Recommendation endpoint returns papers."
        )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    if passed:

        print(
            "DAY 3 - FINAL API VALIDATION PASSED"
        )

        print(
            "=" * 70
        )

        print(
            "Dataset          : READY"
        )

        print(
            "Similarity index : READY"
        )

        print(
            "API metadata     : READY"
        )

        print(
            "API server       : ONLINE"
        )

        print(
            "Search           : WORKING"
        )

        print(
            "Recommendations  : WORKING"
        )

        print(
            "Health check     : PASSED"
        )

        print(
            "Day 3 status     : COMPLETED"
        )

    else:

        print(
            "DAY 3 - FINAL API VALIDATION FAILED"
        )

        print(
            "Review the failed checks above."
        )

    print(
        "=" * 70
    )


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    main()