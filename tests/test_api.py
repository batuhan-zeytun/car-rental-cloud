import pytest

from app import create_app
from app.extensions import db


class TestConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    APP_NAME = "Car Rental Cloud Test"
    APP_VERSION = "test"
    APP_ENV = "test"
    LOG_LEVEL = "CRITICAL"
    REDIS_URL = ""
    AUTO_CREATE_DB = True
    SEED_SAMPLE_DATA = False
    CACHE_TTL_SECONDS = 1


@pytest.fixture()
def client():
    app = create_app(TestConfig)
    with app.app_context():
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_health_and_metrics(client):
    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "car_rental_cars_total" in metrics.text


def test_create_rental_and_return_flow(client):
    car = client.post(
        "/api/cars",
        json={
            "plate_number": "06-TST-01",
            "make": "Toyota",
            "model": "Corolla",
            "year": 2024,
            "location": "Ankara",
            "daily_rate": 1500,
        },
    )
    assert car.status_code == 201

    customer = client.post(
        "/api/customers",
        json={
            "full_name": "Test Customer",
            "email": "customer@example.com",
            "phone": "+90 312 000 0000",
        },
    )
    assert customer.status_code == 201

    rental = client.post(
        "/api/rentals",
        json={
            "car_id": car.get_json()["id"],
            "customer_id": customer.get_json()["id"],
            "start_date": "2026-05-20",
            "end_date": "2026-05-22",
        },
    )
    assert rental.status_code == 201
    body = rental.get_json()
    assert body["days"] == 3
    assert body["total_price"] == 4500
    assert body["status"] == "active"

    overlap = client.post(
        "/api/rentals",
        json={
            "car_id": car.get_json()["id"],
            "customer_id": customer.get_json()["id"],
            "start_date": "2026-05-21",
            "end_date": "2026-05-23",
        },
    )
    assert overlap.status_code == 400

    returned = client.post(f"/api/rentals/{body['id']}/return")
    assert returned.status_code == 200
    assert returned.get_json()["status"] == "completed"


def test_validation_errors_are_json(client):
    response = client.post("/api/customers", json={"email": "missing@example.com"})
    assert response.status_code == 400
    assert "error" in response.get_json()
