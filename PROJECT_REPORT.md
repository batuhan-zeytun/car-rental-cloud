# Car Rental Cloud — Project Report

| Field | Detail |
|---|---|
| **Course** | Cloud Computing |
| **Project Title** | Car Rental Cloud — A 12-Factor Cloud-Native Application |
| **Team** | Solo |
| **Student** | Batuhan Zeytun |
| **Submission Date** | 22 May 2026 |
| **GitHub Repository** | https://github.com/batuhan-zeytun/car-rental-cloud |
| **Live Application** | https://web-production-707f1.up.railway.app |
| **Demo Video** | *(link to be added)* |

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Data Model](#6-data-model)
7. [API Design](#7-api-design)
8. [12-Factor App Compliance](#8-12-factor-app-compliance)
9. [CI/CD Pipeline](#9-cicd-pipeline)
10. [Cloud Deployment](#10-cloud-deployment)
11. [Caching Strategy](#11-caching-strategy)
12. [Monitoring & Logging](#12-monitoring--logging)
13. [Testing](#13-testing)
14. [Admin Processes](#14-admin-processes)
15. [Security Considerations](#15-security-considerations)
16. [Conclusion](#16-conclusion)

---

## 1. Abstract

This project implements a **cloud-native car rental management system** following the [12-Factor App](https://12factor.net/) methodology. The application enables a rental company's staff to manage their vehicle fleet, register customers, create and track rental contracts, and monitor system health — all through a modern, responsive web dashboard.

The system is built with Python/Flask, backed by PostgreSQL and Redis, containerized with Docker, and deployed on Railway cloud platform. The entire development lifecycle is automated through a GitHub Actions CI/CD pipeline that runs tests, builds Docker images, and verifies deployment health on every push to the main branch.

---

## 2. Problem Statement

Car rental companies need a reliable way to track vehicle availability, customer records, and active rental contracts in real time. Without a centralized system:

- The **same car may be double-booked** for overlapping dates.
- **Fleet status** (available, rented, under maintenance) becomes inconsistent.
- **Revenue tracking** requires manual calculation across scattered records.
- **Scaling** the operation means adding complexity to manual processes.

This project solves these problems by providing a cloud-hosted, always-available management platform that enforces business rules at the database level and exposes operational data through a clean API.

---

## 3. Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Vehicle fleet management (add, status tracking) | ✅ Implemented |
| 2 | Customer registration | ✅ Implemented |
| 3 | Rental creation with date-overlap prevention | ✅ Implemented |
| 4 | Automatic price calculation (days × daily rate) | ✅ Implemented |
| 5 | Rental return workflow | ✅ Implemented |
| 6 | 12-Factor compliant architecture | ✅ Implemented |
| 7 | Containerization with Docker | ✅ Implemented |
| 8 | Automated CI/CD pipeline | ✅ Implemented |
| 9 | Cloud deployment on a managed platform | ✅ Deployed on Railway |
| 10 | Health/readiness probes and metrics endpoint | ✅ Implemented |
| 11 | Structured JSON logging to stdout | ✅ Implemented |
| 12 | Redis caching for read performance | ✅ Implemented |

---

## 4. System Architecture

The application follows a **stateless three-tier architecture** deployed entirely on Railway cloud platform.

```
┌─────────────────────────────────────────────────────────┐
│                    Railway Cloud                         │
│                                                         │
│  ┌──────────────────┐    ┌────────────┐  ┌──────────┐  │
│  │  Flask/Gunicorn  │───▶│ PostgreSQL │  │  Redis   │  │
│  │  Web Container   │    │  Database  │  │  Cache   │  │
│  │  (2 workers)     │───▶│            │  │          │  │
│  └──────────────────┘    └────────────┘  └──────────┘  │
│           ▲                                             │
│           │ HTTP                                        │
└───────────┼─────────────────────────────────────────────┘
            │
     ┌──────┴──────┐
     │   Browser   │
     │  Dashboard  │
     └─────────────┘

┌─────────────────────────────────────────────────────────┐
│                  GitHub Actions CI/CD                   │
│                                                         │
│  push to main → Run Tests → Build Docker → Health Check │
└─────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

- **Stateless application layer**: The Flask/Gunicorn container holds no in-process state. All persistence lives in PostgreSQL; all session-independent caching lives in Redis. This means the container can be replaced, restarted, or scaled horizontally without data loss.
- **Backing services as attached resources**: PostgreSQL and Redis are accessed entirely via `DATABASE_URL` and `REDIS_URL` environment variables. Swapping the database for a different provider requires only a config change.
- **Single-page dashboard**: The frontend is a plain HTML/CSS/JavaScript application served by Flask. It communicates with the backend exclusively through the REST API, making the UI completely decoupled from server-side rendering.

---

## 5. Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Language** | Python 3.12 | Rapid development, extensive cloud library support |
| **Framework** | Flask 3.0 | Lightweight, explicit, easy to structure as a 12-factor app |
| **WSGI Server** | Gunicorn 22 | Production-grade, multi-worker, handles concurrent requests |
| **ORM** | Flask-SQLAlchemy 3.1 | Clean database abstraction, supports both SQLite (dev) and PostgreSQL (prod) |
| **Database** | PostgreSQL 16 | ACID-compliant, managed by Railway, production-ready |
| **Cache** | Redis 7 | In-memory key-value store for low-latency read caching |
| **Containerization** | Docker | Reproducible builds, environment parity between dev and prod |
| **CI/CD** | GitHub Actions | Native GitHub integration, free for public repositories |
| **Cloud Platform** | Railway | Simple Docker-based deployment, managed PostgreSQL and Redis |
| **Testing** | pytest | Standard Python testing framework |

---

## 6. Data Model

The system has three core entities with clear relationships:

### Entity Relationship

```
Car (1) ──────────── (N) Rental (N) ──────────── (1) Customer
```

### Car

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `plate_number` | String(20) | Unique, Not Null, Indexed |
| `make` | String(60) | Not Null |
| `model` | String(60) | Not Null |
| `year` | Integer | Not Null, ≥ 2000 |
| `location` | String(120) | Not Null |
| `daily_rate` | Numeric(10,2) | Not Null, > 0 |
| `status` | String(20) | CHECK IN ('available','rented','maintenance') |
| `created_at` | DateTime | Auto-set on insert |
| `updated_at` | DateTime | Auto-updated on change |

### Customer

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `full_name` | String(120) | Not Null |
| `email` | String(120) | Unique, Not Null, Indexed |
| `phone` | String(30) | Not Null |
| `created_at` | DateTime | Auto-set on insert |
| `updated_at` | DateTime | Auto-updated on change |

### Rental

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `car_id` | Integer | FK → cars.id, Indexed |
| `customer_id` | Integer | FK → customers.id, Indexed |
| `start_date` | Date | Not Null |
| `end_date` | Date | Not Null |
| `total_price` | Numeric(10,2) | Computed: days × daily_rate |
| `status` | String(20) | CHECK IN ('active','completed','cancelled') |
| `created_at` | DateTime | Auto-set on insert |
| `updated_at` | DateTime | Auto-updated on change |

### Business Rules Enforced at Service Layer

- A car with `status = 'maintenance'` cannot be rented.
- Creating a rental checks for **date overlap** on the same car: if an active rental exists for the car where date ranges intersect, the new rental is rejected with HTTP 400.
- `total_price` is computed server-side: `(end_date − start_date).days × car.daily_rate`.
- Completing a rental (`/return`) sets rental `status = 'completed'` and car `status = 'available'` atomically.

---

## 7. API Design

All endpoints return JSON. Successful creation returns HTTP 201; validation errors return HTTP 400; duplicate values return HTTP 409.

### Health & Observability

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/healthz` | Liveness probe | `{"status":"ok", "version":"...", "environment":"..."}` |
| GET | `/readyz` | Readiness probe (checks DB + Redis) | `{"status":"ready", "checks":{"database":"ok","cache":"ok"}}` |
| GET | `/metrics` | Prometheus-format metrics | Plain text gauge metrics |

### Fleet API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cars` | List all cars. Optional `?status=available\|rented\|maintenance` filter. Results are Redis-cached for 30 seconds. |
| POST | `/api/cars` | Add a new car. Required fields: `plate_number`, `make`, `model`, `year`, `location`, `daily_rate`. |
| PATCH | `/api/cars/{id}/status` | Update car status. Body: `{"status": "available\|rented\|maintenance"}`. Invalidates cache. |

### Customer API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customers` | List all customers. |
| POST | `/api/customers` | Register a new customer. Required: `full_name`, `email`, `phone`. |

### Rental API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rentals` | List all rentals. Optional `?status=active\|completed\|cancelled` filter. |
| POST | `/api/rentals` | Create a rental. Required: `car_id`, `customer_id`, `start_date`, `end_date`. Validates overlap and car availability. |
| POST | `/api/rentals/{id}/return` | Complete a rental. Sets rental → completed, car → available. |

### Example: Create Rental

**Request:**
```http
POST /api/rentals
Content-Type: application/json

{
  "car_id": 1,
  "customer_id": 2,
  "start_date": "2026-05-24",
  "end_date": "2026-05-27"
}
```

**Response (201 Created):**
```json
{
  "id": 5,
  "car": {"id": 1, "plate_number": "06-AYBU-01", "make": "Toyota", "model": "Corolla"},
  "customer": {"id": 2, "full_name": "Ahmet Yilmaz"},
  "start_date": "2026-05-24",
  "end_date": "2026-05-27",
  "days": 3,
  "total_price": 4500.00,
  "status": "active"
}
```

---

## 8. 12-Factor App Compliance

This section maps each of the twelve factors to a concrete implementation in the project.

### Factor I — Codebase
> *One codebase tracked in revision control, many deploys.*

The entire application lives in a **single GitHub repository** (`batuhan-zeytun/car-rental-cloud`). The same codebase is used for local development (SQLite), CI testing (in-memory SQLite), and production (PostgreSQL on Railway). Different environments are not different codebases — they are the same code configured differently via environment variables.

### Factor II — Dependencies
> *Explicitly declare and isolate dependencies.*

All Python dependencies are declared in `requirements.txt` with pinned versions:
```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
gunicorn==22.0.0
psycopg[binary]==3.2.1
redis==5.0.7
pytest==8.3.2
```
The Docker image installs these from scratch every build. No dependency is assumed to be pre-installed on the host system.

### Factor III — Config
> *Store config in the environment.*

**Zero configuration is hardcoded.** All environment-specific settings are read from environment variables at startup via `app/config.py`:

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///car_rental.db` |
| `REDIS_URL` | Redis connection string | *(empty = disabled)* |
| `SECRET_KEY` | Flask session secret | `dev-secret-change-me` |
| `APP_ENV` | Runtime environment label | `development` |
| `LOG_LEVEL` | Logging threshold | `INFO` |
| `SEED_SAMPLE_DATA` | Load sample data on startup | `true` |

In production (Railway), these are injected as service environment variables. The application never reads from `.env` files in production.

### Factor IV — Backing Services
> *Treat backing services as attached resources.*

PostgreSQL and Redis are treated as **attached resources accessed via URLs**. The application does not care whether the database is running locally in Docker or on Railway's managed infrastructure — the only difference is the value of `DATABASE_URL`. Switching from Railway PostgreSQL to AWS RDS would require changing one environment variable, nothing else.

### Factor V — Build, Release, Run
> *Strictly separate build and run stages.*

The three stages are enforced by the CI/CD pipeline:

- **Build:** GitHub Actions builds the Docker image tagged with the git SHA (`car-rental-cloud:<SHA>`).
- **Release:** Railway combines the built image with production environment variables to create a release.
- **Run:** Railway starts the container with `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 wsgi:app`. The running container is never modified; changes require a new build.

### Factor VI — Processes
> *Execute the app as one or more stateless, share-nothing processes.*

The Flask/Gunicorn container is **fully stateless**. It holds no in-memory state that would be lost on restart:

- No server-side sessions or sticky sessions.
- No local file storage (no uploads, no SQLite in production).
- All persistent data lives in PostgreSQL.
- All cached data lives in Redis (and is re-computable from PostgreSQL if lost).

Any container restart or horizontal scale-out is safe because there is nothing to lose.

### Factor VII — Port Binding
> *Export services via port binding.*

The application is self-contained and exports HTTP via port binding. Gunicorn binds to `0.0.0.0:$PORT` where `$PORT` is injected by Railway at runtime. The application does not rely on any external web server (no Apache/Nginx in front); it is the HTTP server itself.

### Factor VIII — Concurrency
> *Scale out via the process model.*

Gunicorn runs with **2 worker processes and 4 threads per worker**, giving a concurrency of up to 8 simultaneous requests per container. Because the application is stateless (Factor VI), scaling horizontally by adding more Railway replicas requires no code changes — each replica runs identically and shares the same PostgreSQL and Redis backing services.

### Factor IX — Disposability
> *Maximize robustness with fast startup and graceful shutdown.*

- **Fast startup:** The Docker image uses `python:3.12-slim` as base, keeping image size small. Database tables are created at startup only if they do not exist (`AUTO_CREATE_DB`). Typical startup time is under 5 seconds.
- **Health checks:** Railway monitors `/healthz` to detect failed containers and replace them automatically.
- **Graceful shutdown:** Gunicorn handles `SIGTERM` by finishing in-flight requests before exiting, preventing abrupt connection termination.

### Factor X — Dev/Prod Parity
> *Keep development, staging, and production as similar as possible.*

| Concern | Development | Production |
|---------|------------|------------|
| Runtime | Docker container | Docker container (same image) |
| Database | SQLite (file) | PostgreSQL (managed) |
| Cache | Redis disabled | Redis (managed) |
| Config | `.env.example` values | Railway environment variables |

The same Docker image runs in both environments. The only differences are backing service connections controlled via environment variables.

### Factor XI — Logs
> *Treat logs as event streams.*

The application **never writes to log files**. All logs are written to `stdout` as newline-delimited JSON:

```json
{"level": "INFO", "message": "{\"method\": \"POST\", \"path\": \"/api/rentals\", \"status\": 201, \"duration_ms\": 12.4}", "logger": "app"}
```

Every HTTP request is logged with method, path, status code, and duration. Railway captures these stdout streams and makes them available in the deployment log viewer — compatible with any log aggregation system (ELK, Datadog, CloudWatch).

### Factor XII — Admin Processes
> *Run admin/management tasks as one-off processes.*

Database administration and maintenance tasks are implemented as **Flask CLI commands** that run in the same environment as the application but as isolated, one-off processes:

```bash
# Create all database tables
flask init-db

# Seed the database with sample fleet and customer data
flask seed-db

# Print current fleet and rental statistics to stdout
flask stats

# Drop all tables (with confirmation prompt)
flask drop-db
```

These commands use the same `DATABASE_URL` environment variable as the application, ensuring they always operate on the correct database instance.

---

## 9. CI/CD Pipeline

The CI/CD pipeline is defined in `.github/workflows/ci.yml` and runs automatically on every push to the `main` branch and on all pull requests.

### Pipeline Stages

```
Push to main
    │
    ▼
┌─────────────┐
│    test      │  Python 3.12, pytest, SQLite in-memory
│   (14s)      │  → Runs all unit and integration tests
└──────┬──────┘
       │ (pass only)
       ▼
┌─────────────┐
│ docker-build │  Builds Docker image tagged with git SHA
│   (15s)      │  → Verifies Dockerfile and all dependencies install correctly
└──────┬──────┘
       │ (pass only)
       ▼
┌─────────────┐
│   deploy    │  Railway auto-deploys on GitHub push
│   (33s)     │  → Verifies /healthz returns 200 OK
└─────────────┘
```

### Pipeline Configuration

```yaml
jobs:
  test:        # Run pytest with in-memory SQLite, no Redis
  docker-build: # Build Docker image (needs: test)
  deploy:       # Health check verification (needs: docker-build, main branch only)
```

The pipeline enforces that **no code reaches production without passing tests**. The deploy stage waits 30 seconds for Railway's automatic deployment to complete, then calls `/healthz` to confirm the application is healthy.

### Railway Auto-Deploy

Railway is connected directly to the GitHub repository. Every push to `main` triggers an automatic Docker build and deployment on Railway's infrastructure, ensuring the live application always reflects the latest passing commit.

---

## 10. Cloud Deployment

### Platform: Railway

The application is deployed on **Railway** ([railway.app](https://railway.app)), a managed cloud platform that provides:

- Automated Docker builds from GitHub
- Managed PostgreSQL with automatic backups
- Managed Redis
- Environment variable management with secret injection
- Automatic HTTPS with custom domain support
- Health check monitoring and auto-restart

### Deployed Services

| Service | Type | Purpose |
|---------|------|---------|
| `web` | Docker container | Flask/Gunicorn application |
| `Postgres` | Managed PostgreSQL 16 | Persistent data storage |
| `Redis` | Managed Redis 7 | Read cache layer |

### Environment Variables (Production)

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Injected by Railway from Postgres service |
| `REDIS_URL` | Injected by Railway from Redis service |
| `SECRET_KEY` | Manually set in Railway Variables |
| `APP_ENV` | `production` |
| `SEED_SAMPLE_DATA` | `true` (initial data for demo) |

### Dockerfile

```dockerfile
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
RUN useradd --create-home appuser
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/instance && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["sh", "start.sh"]
```

Security best practices applied:
- Non-root user (`appuser`) runs the process.
- `PYTHONDONTWRITEBYTECODE` prevents `.pyc` file accumulation.
- `PYTHONUNBUFFERED` ensures logs reach stdout immediately without buffering.

---

## 11. Caching Strategy

Redis caching is applied to the **car listing endpoint** (`GET /api/cars`), which is the most frequently called read endpoint in the dashboard.

### Cache Key Design

```
cars:list:all         → all cars (no status filter)
cars:list:available   → only available cars
cars:list:rented      → only rented cars
cars:list:maintenance → only maintenance cars
```

### Cache Invalidation

The cache is invalidated on any write operation that changes car data:
- Adding a new car → deletes `cars:list:all` and `cars:list:<status>`
- Updating car status → deletes all four cache keys
- Creating a rental → deletes `cars:list:all`, `cars:list:available`, `cars:list:rented`
- Returning a rental → same as above

### Graceful Degradation

If Redis is unavailable (network issue, restart), the application **continues to work normally** — every request simply fetches fresh data from PostgreSQL. The Redis connection failure is logged as a warning and the `redis_client` is set to `None`, causing all cache operations to be no-ops.

---

## 12. Monitoring & Logging

### Health Endpoints

| Endpoint | Purpose | Used By |
|----------|---------|---------|
| `/healthz` | Liveness: is the app process running? | Railway health check, CI/CD verification |
| `/readyz` | Readiness: can the app serve traffic? (checks DB + Redis) | Load balancer, monitoring |

**`/readyz` response example:**
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

### Prometheus Metrics

The `/metrics` endpoint exposes application metrics in **Prometheus text format**:

```
# HELP car_rental_cars_total Number of cars by status
# TYPE car_rental_cars_total gauge
car_rental_cars_total{status="available"} 4
car_rental_cars_total{status="rented"} 2
car_rental_cars_total{status="maintenance"} 1

# HELP car_rental_rentals_total Number of rentals by status
# TYPE car_rental_rentals_total gauge
car_rental_rentals_total{status="active"} 2
car_rental_rentals_total{status="completed"} 5
car_rental_rentals_total{status="cancelled"} 1
```

These metrics are also **visualized in the dashboard** as animated progress bars, giving operators an at-a-glance view of fleet utilization.

### Structured Logging

Every HTTP request produces a structured JSON log line:

```json
{
  "level": "INFO",
  "message": "{\"method\":\"POST\",\"path\":\"/api/rentals\",\"status\":201,\"duration_ms\":18.3}",
  "logger": "app"
}
```

Logs are written to `stdout` (Factor XI) and captured by Railway's log aggregation system. The JSON structure allows easy parsing and filtering in any log management tool.

---

## 13. Testing

Tests are located in `tests/test_api.py` and run with `pytest` using an in-memory SQLite database (no external dependencies required).

### Test Coverage

| Test | What it verifies |
|------|-----------------|
| `test_health` | `/healthz` returns `{"status": "ok"}` with HTTP 200 |
| `test_metrics` | `/metrics` returns Prometheus-format plain text |
| `test_full_rental_flow` | Create car → Create customer → Create rental → Verify price calculation → Return rental → Verify status changes |
| `test_overlap_prevention` | Two rentals for the same car with overlapping dates → second request returns HTTP 400 |
| `test_validation_errors` | Missing required fields → HTTP 400 with JSON error message |

### Running Tests

```bash
# Locally
pytest -v

# In CI (GitHub Actions)
DATABASE_URL=sqlite:///:memory: AUTO_CREATE_DB=true SEED_SAMPLE_DATA=false pytest -q
```

### Test Configuration

The test suite uses a Flask test client with:
- In-memory SQLite (no persistent state between test runs)
- Redis disabled (cache gracefully skipped)
- `AUTO_CREATE_DB=true` (tables created fresh for each test session)
- `SEED_SAMPLE_DATA=false` (clean database, test data added explicitly)

---

## 14. Admin Processes

Following Factor XII, administrative tasks are implemented as Flask CLI commands that run as isolated one-off processes in the same environment as the application.

### Available Commands

```bash
# Initialize database (create all tables)
flask init-db

# Seed database with sample data
flask seed-db

# Print fleet and rental statistics
flask stats
# Output:
# ── Fleet stats ──────────────────
#   available      4
#   rented         2
#   maintenance    1
#
# ── Rental stats ─────────────────
#   active         2
#   completed      5
#   cancelled      1

# Drop all tables (requires confirmation)
flask drop-db
# > This will delete all data. Are you sure? [y/N]:
```

These commands use the same `DATABASE_URL` environment variable as the running application, ensuring they always operate on the correct database. They can be executed remotely via Railway's CLI (`railway run flask stats`) or locally against any configured database.

---

## 15. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Secret management | `SECRET_KEY` and `DATABASE_URL` stored as Railway environment secrets, never in source code |
| SQL injection | All database queries use SQLAlchemy ORM parameterized queries |
| Non-root container | Docker container runs as `appuser`, not `root` |
| Input validation | All API inputs validated before database write; type checking enforced |
| Integrity errors | Duplicate email / plate number returns HTTP 409 without leaking internal error details |
| Database constraints | `CHECK` constraints on status columns enforced at database level |

---

## 16. Conclusion

Car Rental Cloud successfully demonstrates a production-grade, cloud-native application built according to all twelve factors of the 12-Factor App methodology. The project covers the full spectrum of cloud application development:

- **Application development** with Python/Flask following clean architectural principles
- **Containerization** with Docker for environment parity and reproducible builds
- **Cloud deployment** on Railway with managed PostgreSQL and Redis
- **CI/CD automation** with GitHub Actions — tests, Docker build, and health verification on every push
- **Observability** through health endpoints, Prometheus metrics, structured JSON logging, and a live metrics dashboard
- **Operational tooling** through Flask CLI admin commands for database management

The live application is accessible at **https://web-production-707f1.up.railway.app** and the complete source code is available at **https://github.com/batuhan-zeytun/car-rental-cloud**.

---

*Report prepared for Cloud Computing course, May 2026.*
