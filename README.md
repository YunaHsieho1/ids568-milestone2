# ML Inference Service (Milestone 2)

Minimal containerized ML inference API with CI/CD.

[![Build and Push](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/build.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/build.yml)

## Quick start (local development)

```bash
# Clone and enter repo
cd jason222

# Create venv (optional)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install deps and run
pip install -r app/requirements.txt
python app/app.py
```

Service runs at `http://localhost:8080`.

- Health: `curl http://localhost:8080/health`
- Predict: `curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"features": [1,2,3]}'`

## Run with Docker

```bash
# Build
docker build -t ml-service:0.1.0 .

# Run
docker run -p 8080:8080 ml-service:0.1.0
```

Or with Compose:

```bash
docker compose up --build
```

## Pull and run (from registry)

After the image is pushed to the course registry (see RUNBOOK.md):

```bash
# Replace with your registry and tag from the course
docker pull <REGISTRY>/<YOUR_NAMESPACE>/ml-service:v0.1.0
docker run -p 8080:8080 <REGISTRY>/<YOUR_NAMESPACE>/ml-service:v0.1.0
```

## API

| Method | Path     | Body                     | Description        |
|--------|----------|--------------------------|--------------------|
| GET    | `/health`| —                        | Health check       |
| POST   | `/predict` | `{"features": [float, ...]}` | Returns `{"prediction": float}` |

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## CI/CD

- **Test**: every push/PR runs `pytest tests/`.
- **Build**: on push to `main`/`master`, Docker image is built.
- **Publish**: on version tags (e.g. `v0.1.0`), image is pushed to the configured registry.
- **GCP Artifact Registry**: step-by-step setup → [docs/GCP_ARTIFACT_REGISTRY_SETUP.md](docs/GCP_ARTIFACT_REGISTRY_SETUP.md). Other registries: see RUNBOOK.md for secrets.

## Project layout

```
.
├── app/
│   ├── app.py
│   └── requirements.txt
├── tests/
│   └── test_app.py
├── .github/workflows/build.yml
├── Dockerfile
├── docker-compose.yaml
├── requirements-dev.txt
└── README.md
```
