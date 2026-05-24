# Car Rental Cloud

A 12-factor car rental management application built for a cloud computing course.
It provides a small operations dashboard plus REST APIs for fleet inventory,
customers, rentals, health checks, metrics, logging, Docker deployment, and CI.

## Tech Stack

- **Language / Framework:** Python 3.12, Flask
- **Database:** PostgreSQL in Docker/cloud, SQLite for quick local development
- **Caching:** Redis, optional and controlled by `REDIS_URL`
- **Deployment:** Docker container, Google Cloud Run sample manifest, PaaS `Procfile`
- **CI/CD:** GitHub Actions
- **Monitoring:** `/healthz`, `/readyz`, `/metrics`, container healthcheck
- **Logging:** JSON logs to stdout/stderr for cloud log collectors

## Features

- Fleet inventory: add cars and update status as available, rented, or maintenance
- Customer registry: add and list customers
- Rental workflow: create rentals, prevent overlapping active bookings, return cars
- Web dashboard at `/`
- REST API under `/api`
- Health and readiness probes
- Prometheus-style metrics endpoint
- Environment-based configuration for 12-factor compliance

## Quick Start

### Option 1: Local Python

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:8000`.

On Windows, you can also run:

```bat
scripts\start-dev.bat
```

### Option 2: Docker Compose

```bash
docker compose up --build
```

Open `http://127.0.0.1:8000`.

Docker Compose starts:

- `web`: Flask/Gunicorn application
- `db`: PostgreSQL
- `redis`: Redis cache

## Environment Variables

Copy `.env.example` when you need a local environment file.

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | Runtime environment label, for example `development`, `ci`, `production` |
| `APP_VERSION` | Version shown by health checks |
| `SECRET_KEY` | Flask secret key |
| `PORT` | HTTP port |
| `DATABASE_URL` | SQLAlchemy-compatible database URL |
| `REDIS_URL` | Redis URL; leave empty to disable cache |
| `AUTO_CREATE_DB` | Creates tables at startup for demo use |
| `SEED_SAMPLE_DATA` | Seeds sample cars/customers |
| `LOG_LEVEL` | Logging threshold |

## API Examples

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
curl http://127.0.0.1:8000/metrics
curl http://127.0.0.1:8000/api/cars
```

Create a car:

```bash
curl -X POST http://127.0.0.1:8000/api/cars ^
  -H "Content-Type: application/json" ^
  -d "{\"plate_number\":\"06-AYBU-02\",\"make\":\"Ford\",\"model\":\"Focus\",\"year\":2024,\"location\":\"Ankara\",\"daily_rate\":1500}"
```

See `docs/api-examples.http` for more requests.

## 12-Factor Mapping

| Factor | Implementation |
| --- | --- |
| Codebase | Single Git repository with app, tests, Docker, docs, and CI |
| Dependencies | Explicit `requirements.txt`; containerized runtime |
| Config | Runtime config through environment variables |
| Backing services | Database and cache attached via `DATABASE_URL` and `REDIS_URL` |
| Build, release, run | CI tests/builds; Docker image is the deployable artifact |
| Processes | Stateless HTTP process; data stored in backing services |
| Port binding | Gunicorn binds to `$PORT` |
| Concurrency | Gunicorn workers/threads configurable by env vars |
| Disposability | Fast startup, health checks, graceful container replacement |
| Dev/prod parity | Same container runs locally and in cloud |
| Logs | JSON logs emitted to stdout |
| Admin processes | Seeding and table creation are env-controlled release/demo operations |

## Tests

```bash
pytest -q
```

## Project Delivery Files

- `PROJECT_REPORT_TR.md`: Turkish project report draft
- `docs/demo-video-script.md`: Demo recording flow
- `docs/deployment-google-cloud.md`: Cloud Run deployment guide
- `docs/project-proposal-tr.md`: Proposal text
- `.github/workflows/ci.yml`: CI pipeline
