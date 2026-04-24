import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "backend"


def test_health_content_type(client):
    res = client.get("/health")
    assert res.content_type == "application/json"


def test_unknown_route_returns_404(client):
    res = client.get("/does-not-exist")
    assert res.status_code == 404
