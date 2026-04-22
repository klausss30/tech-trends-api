from app import create_app


def test_health_endpoint_lists_available_routes():
    app = create_app()

    response = app.test_client().get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == 200
    assert payload["data"]["status"] == "ok"
    assert "/api/top-repositories?since=daily" in payload["data"]["endpoints"]


def test_invalid_since_returns_bad_request():
    app = create_app()

    response = app.test_client().get("/api/keywords?since=yearly")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["code"] == 400
    assert "Invalid since value" in payload["message"]
