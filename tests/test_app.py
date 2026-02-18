"""Unit tests for ML inference service (Milestone 2)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.app import app


def test_health_returns_ok():
    """GET /health returns 200 and status ok."""
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data == {"status": "ok"}


def test_predict_valid_input():
    """POST /predict with valid features returns prediction."""
    client = app.test_client()
    r = client.post(
        "/predict",
        json={"features": [1.0, 2.0, 3.0]},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert "prediction" in data
    assert data["prediction"] == 2.0


def test_predict_valid_integers():
    """POST /predict accepts integers in features."""
    client = app.test_client()
    r = client.post("/predict", json={"features": [10, 20]})
    assert r.status_code == 200
    assert r.get_json()["prediction"] == 15.0


def test_predict_missing_features():
    """POST /predict without features returns 400."""
    client = app.test_client()
    r = client.post("/predict", json={})
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data and "features" in data["error"].lower()


def test_predict_invalid_features_not_list():
    """POST /predict with non-list features returns 400."""
    client = app.test_client()
    r = client.post("/predict", json={"features": "not-a-list"})
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data


def test_predict_invalid_features_not_numbers():
    """POST /predict with non-numeric values returns 400."""
    client = app.test_client()
    r = client.post("/predict", json={"features": [1, "two", 3]})
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data
