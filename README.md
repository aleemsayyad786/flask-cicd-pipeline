# Flask CI/CD Pipeline 🚀

A **production-grade CI/CD pipeline** built with GitHub Actions, Docker, and Python Flask.  
This project demonstrates real-world DevOps practices used daily in software companies —  
automated testing, containerization, vulnerability scanning, and multi-arch Docker deployments.

![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/aleemsayyad786/flask-cicd-pipeline/ci-cd.yml?label=CI%2FCD&style=flat-square)
![Docker Pulls](https://img.shields.io/docker/pulls/aleemsayyad786/flask-cicd-demo?style=flat-square)
![Coverage](https://img.shields.io/badge/coverage-80%25%2B-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## Pipeline Overview

```
┌─────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Git Push   │───▶│  Lint Check  │───▶│  Test Matrix     │───▶│ Docker Build │
│  (main/PR)  │    │  (Flake8)    │    │  (Py 3.11/3.12)  │    │ + Trivy Scan │
└─────────────┘    └──────────────┘    └──────────────────┘    └──────┬───────┘
                                                                        │
                                                               ┌────────▼───────┐
                                                               │  Push Docker   │
                                                               │  Hub (main)    │
                                                               └────────────────┘
```

**Every push triggers automatically:**
1. **Lint** — Flake8 catches syntax errors and code style issues
2. **Test** — Pytest runs against Python 3.11 and 3.12 with ≥80% coverage enforced
3. **Docker Build** — Multi-stage build produces a minimal, hardened image
4. **Security Scan** — Trivy scans for CRITICAL/HIGH CVEs and fails the pipeline if found
5. **Push** — Pushes `latest`, `main`, and `sha-<short>` tags to Docker Hub (main branch only)

---

## Tech Stack

| Layer        | Technology                             |
|-------------|----------------------------------------|
| App          | Python 3.12, Flask 3, Gunicorn         |
| CI/CD        | GitHub Actions                         |
| Container    | Docker (multi-stage), Docker Compose   |
| Registry     | Docker Hub (multi-arch: amd64 + arm64) |
| Testing      | Pytest, pytest-cov                     |
| Linting      | Flake8, flake8-bugbear                 |
| Security     | Trivy (container vulnerability scan)   |

---

## Project Structure

```
flask-cicd-pipeline/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml          # Main pipeline (lint → test → build → push)
│       └── pr-checks.yml      # Fast checks on pull requests
├── app/
│   ├── __init__.py
│   └── main.py                # Flask app (health, CRUD API)
├── tests/
│   └── test_api.py            # Full pytest suite (20+ tests)
├── Dockerfile                 # Multi-stage production build
├── docker-compose.yml         # Local dev environment
├── Makefile                   # Developer shortcuts
├── pyproject.toml             # Pytest + coverage config
└── requirements.txt
```

---

## Quick Start

### Run locally (Docker)

```bash
git clone https://github.com/aleemsayyad786/flask-cicd-pipeline.git
cd flask-cicd-pipeline

# Start with Docker Compose
make run

# App is live at:
curl http://localhost:5000/health
```

### Run locally (Python)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

### Run tests

```bash
make test
# or
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## API Reference

| Method | Endpoint            | Description          |
|--------|---------------------|----------------------|
| GET    | `/`                 | App info             |
| GET    | `/health`           | Liveness probe       |
| GET    | `/ready`            | Readiness probe      |
| GET    | `/api/v1`           | API overview         |
| GET    | `/api/v1/items`     | List all items       |
| POST   | `/api/v1/items`     | Create an item       |
| GET    | `/api/v1/items/:id` | Get item by ID       |

**Example:**
```bash
# Create an item
curl -X POST http://localhost:5000/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "description": "A sample item"}'

# Response
{
  "id": 1,
  "name": "Widget",
  "description": "A sample item",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Setting Up the Pipeline (Your Fork)

### 1. Fork & clone this repo

```bash
git clone https://github.com/aleemsayyad786/flask-cicd-pipeline.git
```

### 2. Add GitHub Secrets

Go to **Settings → Secrets and Variables → Actions** and add:

| Secret Name           | Value                          |
|-----------------------|-------------------------------|
| `DOCKERHUB_USERNAME`  | Your Docker Hub username       |
| `DOCKERHUB_TOKEN`     | Docker Hub access token (not password) |

> Get a Docker Hub token at: hub.docker.com → Account Settings → Security → New Access Token

### 3. Push to main and watch it run

```bash
git add .
git commit -m "feat: initial CI/CD pipeline setup"
git push origin main
```

Go to the **Actions** tab in your GitHub repo to watch the pipeline execute live.

---

## Docker Hub

Pull the latest image directly:

```bash
docker pull aleemsayyad786/flask-cicd-demo:latest
docker run -p 5000:5000 aleemsayyad786/flask-cicd-demo:latest
```

Images are tagged with:
- `latest` — most recent main branch build
- `main` — same as latest
- `sha-<short>` — pinned to a specific commit (e.g. `sha-a1b2c3d`)

---

## Key DevOps Concepts Demonstrated

- **CI/CD automation** — zero-touch pipeline from push to deployed image
- **Matrix testing** — parallel runs across Python 3.11 and 3.12
- **Multi-stage Docker builds** — smaller, more secure final image
- **Non-root containers** — runs as `appuser`, not `root`
- **OCI image labels** — standard metadata for traceability
- **Vulnerability scanning** — Trivy blocks builds with CRITICAL CVEs
- **Build caching** — GitHub Actions cache cuts build time by ~60%
- **Multi-arch images** — supports both `amd64` (servers) and `arm64` (Apple M1/M2)
- **Concurrency control** — cancels stale in-progress runs on the same branch
- **PR gates** — separate lightweight checks for pull requests
- **Pipeline summaries** — job results posted to the GitHub Actions summary page

---

## License

MIT © [Your Name](https://github.com/aleemsayyad786)
