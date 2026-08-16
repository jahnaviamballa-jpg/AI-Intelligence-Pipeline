from fastapi.testclient import TestClient

from src.api.api_server import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "AI Research Intelligence API"
    assert data["status"] == "online"
    assert data["papers"] == 1000


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["papers"] == 1000


def test_papers_endpoint():
    response = client.get("/papers?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1000
    assert data["returned"] == 5
    assert len(data["papers"]) == 5


def test_search_endpoint():
    response = client.get(
        "/search",
        params={
            "q": "LLM reasoning",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "LLM reasoning"
    assert "count" in data
    assert "results" in data
    assert len(data["results"]) <= 5


def test_search_requires_query():
    response = client.get("/search")

    assert response.status_code == 422


def test_areas_endpoint():
    response = client.get("/areas")

    assert response.status_code == 200

    data = response.json()

    assert "total_areas" in data
    assert "areas" in data
    assert isinstance(data["areas"], dict)


def test_area_endpoint():
    areas_response = client.get("/areas")

    assert areas_response.status_code == 200

    areas = areas_response.json()["areas"]

    assert len(areas) > 0

    area = next(iter(areas))

    response = client.get(
        f"/area/{area}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["area"] == area
    assert "papers" in data
    assert len(data["papers"]) > 0


def test_emerging_endpoint():
    response = client.get(
        "/emerging?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "papers" in data
    assert len(data["papers"]) <= 5


def test_recommendations_endpoint():
    response = client.get(
        "/recommendations?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "papers" in data
    assert len(data["papers"]) <= 5