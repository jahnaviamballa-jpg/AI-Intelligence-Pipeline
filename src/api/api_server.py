import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# =========================================================
# Configuration
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "recommended_research_papers.json"
)

SIMILARITY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "similarity_index.json"
)


# =========================================================
# Load data
# =========================================================

def load_json(path):
    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


print("=" * 70)
print("AI Intelligence Pipeline")
print("Day 3 - Step 6: Research Intelligence API Server")
print("=" * 70)

print("\nLoading research dataset...")

papers = load_json(DATASET_FILE)

print(
    f"Loaded {len(papers)} papers."
)


# =========================================================
# FastAPI application
# =========================================================

app = FastAPI(
    title="AI Research Intelligence API",
    description=(
        "Unified API for AI research search, "
        "recommendations, trends and similarity."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Helper functions
# =========================================================

def normalize(value):
    return str(value).lower().strip()


def search_papers(query, limit=10):

    query_terms = [
        term
        for term in normalize(query).split()
        if term
    ]

    results = []

    for paper in papers:

        searchable_text = " ".join([
            normalize(paper.get("title", "")),
            normalize(paper.get("abstract", "")),
            normalize(paper.get("research_area", "")),
            normalize(paper.get("research_stage", "")),
            normalize(paper.get("keywords", "")),
            normalize(paper.get("topics", "")),
            normalize(paper.get("detected_trends", "")),
        ])

        score = 0

        for term in query_terms:

            if term in searchable_text:
                score += 1

            title = normalize(
                paper.get("title", "")
            )

            if term in title:
                score += 3

        if score > 0:

            result = dict(paper)

            result["search_score"] = score

            results.append(result)

    results.sort(
        key=lambda item:
        item["search_score"],
        reverse=True
    )

    return results[:limit]


def filter_by_area(area, limit=50):

    results = [
        paper
        for paper in papers
        if normalize(
            paper.get("research_area", "")
        ) == normalize(area)
    ]

    return results[:limit]


def get_emerging(limit=50):

    results = [
        paper
        for paper in papers
        if normalize(
            paper.get("research_stage", "")
        ) == "emerging"
    ]

    results.sort(
        key=lambda paper:
        paper.get(
            "recommendation_score",
            0
        ),
        reverse=True
    )

    return results[:limit]


def get_recommendations(limit=10):

    results = sorted(
        papers,
        key=lambda paper:
        paper.get(
            "recommendation_score",
            0
        ),
        reverse=True
    )

    return results[:limit]


# =========================================================
# API routes
# =========================================================

@app.get("/")
def root():

    return {
        "name": "AI Research Intelligence API",
        "version": "1.0.0",
        "status": "online",
        "papers": len(papers),
        "endpoints": [
            "/health",
            "/papers",
            "/search",
            "/areas",
            "/area/{area}",
            "/emerging",
            "/recommendations",
        ],
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "papers": len(papers),
    }


@app.get("/papers")
def get_papers(
    limit: int = Query(
        20,
        ge=1,
        le=100
    )
):

    return {
        "total": len(papers),
        "returned": min(
            limit,
            len(papers)
        ),
        "papers": papers[:limit],
    }


@app.get("/search")
def search(
    q: str = Query(
        ...,
        min_length=1
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50
    )
):

    results = search_papers(
        q,
        limit
    )

    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


@app.get("/areas")
def research_areas():

    areas = {}

    for paper in papers:

        area = paper.get(
            "research_area",
            "Unknown"
        )

        areas[area] = (
            areas.get(area, 0) + 1
        )

    return {
        "total_areas": len(areas),
        "areas": areas,
    }


@app.get("/area/{area}")
def area_papers(
    area: str,
    limit: int = Query(
        50,
        ge=1,
        le=100
    )
):

    results = filter_by_area(
        area,
        limit
    )

    if not results:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No papers found for "
                f"research area: {area}"
            )
        )

    return {
        "area": area,
        "count": len(results),
        "papers": results,
    }


@app.get("/emerging")
def emerging_papers(
    limit: int = Query(
        20,
        ge=1,
        le=100
    )
):

    results = get_emerging(
        limit
    )

    return {
        "count": len(results),
        "papers": results,
    }


@app.get("/recommendations")
def recommendations(
    limit: int = Query(
        10,
        ge=1,
        le=50
    )
):

    results = get_recommendations(
        limit
    )

    return {
        "count": len(results),
        "papers": results,
    }


# =========================================================
# Startup
# =========================================================

if __name__ == "__main__":

    import uvicorn

    print("\n" + "-" * 70)
    print("Starting Research Intelligence API...")
    print("-" * 70)

    print(
        "\nAPI documentation:"
    )

    print(
        "http://127.0.0.1:8000/docs"
    )

    print(
        "\nAPI endpoints:"
    )

    print(
        "GET /health"
    )

    print(
        "GET /papers"
    )

    print(
        "GET /search?q=LLM%20reasoning"
    )

    print(
        "GET /areas"
    )

    print(
        "GET /area/Agentic%20AI"
    )

    print(
        "GET /emerging"
    )

    print(
        "GET /recommendations"
    )

    print("\n" + "=" * 70)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )