# Google Cloud Deployment Guide

This project can run on any container platform. The recommended course demo
deployment is:

- Cloud Run for the Flask/Gunicorn container
- Cloud SQL for PostgreSQL
- Memorystore or another managed Redis service for cache
- Cloud Logging and Cloud Monitoring for logs and metrics
- GitHub Actions for CI

## 1. Build and Push the Image

Replace `PROJECT_ID` and `REGION`.

```bash
gcloud config set project PROJECT_ID
gcloud artifacts repositories create car-rental --repository-format=docker --location=REGION
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/car-rental/car-rental-cloud:latest
```

## 2. Create Secrets

Store sensitive values outside the codebase.

```bash
printf "your-production-secret" | gcloud secrets create car-rental-secret-key --data-file=-
printf "postgresql://USER:PASSWORD@HOST:5432/DB_NAME" | gcloud secrets create car-rental-database-url --data-file=-
```

## 3. Deploy to Cloud Run

You can either edit `deploy/cloud-run-service.yaml` and apply it, or deploy with
CLI flags.

```bash
gcloud run deploy car-rental-cloud \
  --image REGION-docker.pkg.dev/PROJECT_ID/car-rental/car-rental-cloud:latest \
  --region REGION \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars APP_ENV=production,APP_VERSION=0.1.0,AUTO_CREATE_DB=true,SEED_SAMPLE_DATA=false,LOG_LEVEL=INFO \
  --set-secrets SECRET_KEY=car-rental-secret-key:latest,DATABASE_URL=car-rental-database-url:latest
```

## 4. Connect PostgreSQL

For production, create a Cloud SQL PostgreSQL instance and use its connection
string as `DATABASE_URL`.

Recommended production settings:

- `AUTO_CREATE_DB=false` after the first release or after adding migrations
- `SEED_SAMPLE_DATA=false`
- Strong `SECRET_KEY`
- Private database connectivity when the project budget allows it

## 5. Cache

Redis cache is optional. If a managed Redis instance is available, set:

```text
REDIS_URL=redis://HOST:6379/0
```

If `REDIS_URL` is empty, the app continues to work without cache.

## 6. Monitoring and Logs

- `/healthz`: basic liveness check
- `/readyz`: database and cache readiness
- `/metrics`: Prometheus-style fleet/rental counts
- stdout JSON logs: automatically collected by cloud logging systems

## 7. Smoke Test

After deployment:

```bash
curl https://SERVICE_URL/healthz
curl https://SERVICE_URL/readyz
curl https://SERVICE_URL/metrics
curl https://SERVICE_URL/api/cars
```

