import os
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENV = os.getenv("FLASK_ENV", "production")


# ──────────────────────────────────────────
# Health & Readiness  (used by Kubernetes / load balancers)
# ──────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Liveness probe — is the process alive?"""
    return jsonify({
        "status": "healthy",
        "version": APP_VERSION,
        "environment": ENV,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route("/ready", methods=["GET"])
def ready():
    """Readiness probe — is the app ready to serve traffic?"""
    return jsonify({
        "status": "ready",
        "version": APP_VERSION
    }), 200


# ──────────────────────────────────────────
# Core API
# ──────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "app": "Flask CI/CD Demo",
        "version": APP_VERSION,
        "environment": ENV,
        "message": "Pipeline is live 🚀",
        "docs": "/api/v1"
    }), 200


@app.route("/api/v1", methods=["GET"])
def api_info():
    return jsonify({
        "version": "v1",
        "endpoints": [
            {"method": "GET",  "path": "/",          "description": "App info"},
            {"method": "GET",  "path": "/health",    "description": "Liveness probe"},
            {"method": "GET",  "path": "/ready",     "description": "Readiness probe"},
            {"method": "GET",  "path": "/api/v1",    "description": "API overview"},
            {"method": "GET",  "path": "/api/v1/items",   "description": "List all items"},
            {"method": "POST", "path": "/api/v1/items",   "description": "Create an item"},
            {"method": "GET",  "path": "/api/v1/items/<id>", "description": "Get single item"},
        ]
    }), 200


# In-memory store (swap with a real DB in production)
_items: dict = {}
_next_id: int = 1


@app.route("/api/v1/items", methods=["GET"])
def list_items():
    return jsonify({
        "count": len(_items),
        "items": list(_items.values())
    }), 200


@app.route("/api/v1/items", methods=["POST"])
def create_item():
    global _next_id
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        return jsonify({"error": "Field 'name' is required"}), 400

    item = {
        "id": _next_id,
        "name": data["name"],
        "description": data.get("description", ""),
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    _items[_next_id] = item
    _next_id += 1
    return jsonify(item), 201


@app.route("/api/v1/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = _items.get(item_id)
    if not item:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item), 200


# ──────────────────────────────────────────
# Error handlers
# ──────────────────────────────────────────

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Route not found"}), 404


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=(ENV == "development"))
