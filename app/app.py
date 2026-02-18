"""
Minimal ML inference service for Milestone 2.
Exposes a /predict endpoint that returns a dummy prediction.
"""
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Minimal "model": returns prediction from input features (sum as placeholder)
def predict(features: list[float]) -> float:
    """Placeholder inference: return sum of features as prediction."""
    return sum(features) / len(features) if features else 0.0


@app.route("/health", methods=["GET"])
def health():
    """Health check for CI/container orchestration."""
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def inference():
    """
    Expects JSON: {"features": [float, ...]}
    Returns JSON: {"prediction": float}
    """
    data = request.get_json(silent=True)
    if not data or "features" not in data:
        return jsonify({"error": "Missing 'features' in body"}), 400
    features = data["features"]
    if not isinstance(features, list) or not all(isinstance(x, (int, float)) for x in features):
        return jsonify({"error": "features must be a list of numbers"}), 400
    pred = predict(features)
    return jsonify({"prediction": pred})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
