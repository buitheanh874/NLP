import pytest


pytest.importorskip("fastapi")
pytest.importorskip("starlette")

from fastapi.testclient import TestClient

from webapp.main import app


def test_webapp_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webapp_root_serves_html():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_webapp_catalog_endpoint():
    client = TestClient(app)
    response = client.get("/api/catalog")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)


def test_webapp_review_pool_endpoint():
    client = TestClient(app)
    response = client.get("/api/review_pool?limit=5")
    assert response.status_code == 200
    payload = response.json()
    assert "source" in payload
    assert "count" in payload
    assert "reviews" in payload
    assert isinstance(payload["reviews"], list)
    assert payload["count"] == len(payload["reviews"])
    assert payload["count"] <= 5
    if payload["reviews"]:
        first = payload["reviews"][0]
        assert "issue_flags" in first
        assert isinstance(first["issue_flags"], dict)
