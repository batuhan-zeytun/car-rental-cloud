# Demo Video Script

Recommended length: 5-7 minutes.

## 1. Intro

- Show the GitHub repository.
- Mention the course requirement: 12-factor app running on a cloud provider.
- Introduce the project: Car Rental Cloud.

## 2. Architecture

- Open `README.md` and show the tech stack.
- Mention Flask, PostgreSQL, Redis, Docker, GitHub Actions, health checks,
  metrics, and JSON logging.
- Open `PROJECT_REPORT_TR.md` and briefly show the 12-factor table.

## 3. Local Run

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000
```

## 4. Dashboard Flow

- Show available cars on the dashboard.
- Add a new customer.
- Add a new car.
- Create a rental.
- Show that the car status changes to `rented`.
- Try to create an overlapping rental for the same car and show the error.
- Return the rental and show that the status changes to `completed`.

## 5. API / Cloud-Native Endpoints

Open these endpoints in the browser or terminal:

```text
/healthz
/readyz
/metrics
/api/cars
/api/rentals
```

Explain that:

- `/healthz` is used for container health checks.
- `/readyz` checks backing service readiness.
- `/metrics` can be scraped by Prometheus or monitored by cloud tools.
- Logs are emitted as JSON to stdout.

## 6. CI/CD

- Open `.github/workflows/ci.yml`.
- Explain that tests run on push/pull request.
- Show a successful GitHub Actions run if available.

## 7. Cloud Deployment

- Open `docs/deployment-google-cloud.md`.
- Explain container image, Cloud Run, Cloud SQL, Redis/Memorystore, and Cloud
  Logging.
- If deployed, open the cloud URL and repeat a short rental flow.

## 8. Closing

- Summarize 12-factor compliance.
- Mention future improvements: authentication, payment integration, email
  notifications, and database migrations.

