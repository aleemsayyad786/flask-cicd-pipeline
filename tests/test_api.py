"""
Test suite for Flask CI/CD Demo API.
Run: pytest tests/ -v --cov=app --cov-report=term-missing
"""
import json
import pytest
from app.main import app


# ──────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_items():
    """Clear in-memory store before every test for isolation."""
    import app.main as m
    m._items.clear()
    m._next_id = 1
    yield


# ──────────────────────────────────────────
# Health & Readiness
# ──────────────────────────────────────────

class TestHealthEndpoints:

    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_has_required_fields(self, client):
        data = r = client.get("/health").get_json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "environment" in data

    def test_ready_returns_200(self, client):
        r = client.get("/ready")
        assert r.status_code == 200

    def test_ready_payload(self, client):
        data = client.get("/ready").get_json()
        assert data["status"] == "ready"


# ──────────────────────────────────────────
# Root & API Info
# ──────────────────────────────────────────

class TestRootAndInfo:

    def test_root_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_root_contains_app_name(self, client):
        data = client.get("/").get_json()
        assert "app" in data
        assert "version" in data

    def test_api_info_lists_endpoints(self, client):
        data = client.get("/api/v1").get_json()
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)
        assert len(data["endpoints"]) > 0


# ──────────────────────────────────────────
# Items CRUD
# ──────────────────────────────────────────

class TestListItems:

    def test_list_empty_initially(self, client):
        data = client.get("/api/v1/items").get_json()
        assert data["count"] == 0
        assert data["items"] == []

    def test_list_after_create(self, client):
        client.post("/api/v1/items",
                    data=json.dumps({"name": "Widget"}),
                    content_type="application/json")
        data = client.get("/api/v1/items").get_json()
        assert data["count"] == 1


class TestCreateItem:

    def test_create_returns_201(self, client):
        r = client.post("/api/v1/items",
                        data=json.dumps({"name": "Widget"}),
                        content_type="application/json")
        assert r.status_code == 201

    def test_create_returns_item(self, client):
        r = client.post("/api/v1/items",
                        data=json.dumps({"name": "Widget", "description": "A test widget"}),
                        content_type="application/json")
        data = r.get_json()
        assert data["name"] == "Widget"
        assert data["description"] == "A test widget"
        assert "id" in data
        assert "created_at" in data

    def test_create_auto_increments_id(self, client):
        payload = lambda n: json.dumps({"name": n})
        ct = "application/json"
        id1 = client.post("/api/v1/items", data=payload("A"), content_type=ct).get_json()["id"]
        id2 = client.post("/api/v1/items", data=payload("B"), content_type=ct).get_json()["id"]
        assert id2 == id1 + 1

    def test_create_missing_name_returns_400(self, client):
        r = client.post("/api/v1/items",
                        data=json.dumps({"description": "no name"}),
                        content_type="application/json")
        assert r.status_code == 400
        assert "error" in r.get_json()

    def test_create_no_body_returns_400(self, client):
        r = client.post("/api/v1/items", content_type="application/json")
        assert r.status_code == 400

    def test_create_optional_description_defaults_to_empty(self, client):
        r = client.post("/api/v1/items",
                        data=json.dumps({"name": "No desc"}),
                        content_type="application/json")
        assert r.get_json()["description"] == ""


class TestGetItem:

    def test_get_existing_item(self, client):
        create = client.post("/api/v1/items",
                             data=json.dumps({"name": "Gadget"}),
                             content_type="application/json").get_json()
        r = client.get(f"/api/v1/items/{create['id']}")
        assert r.status_code == 200
        assert r.get_json()["name"] == "Gadget"

    def test_get_missing_item_returns_404(self, client):
        r = client.get("/api/v1/items/9999")
        assert r.status_code == 404
        assert "error" in r.get_json()


# ──────────────────────────────────────────
# Error Handlers
# ──────────────────────────────────────────

class TestErrorHandlers:

    def test_unknown_route_returns_404(self, client):
        r = client.get("/does-not-exist")
        assert r.status_code == 404
        assert "error" in r.get_json()
