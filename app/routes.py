import json
import time

from flask import Response, current_app, jsonify, render_template, request
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from .cache import cache_delete, cache_get_json, cache_set_json
from .extensions import db
from .models import Car, Customer, Rental
from .services import (
    ValidationError,
    complete_rental,
    create_car,
    create_customer,
    create_rental,
    update_car_status,
)


def _json_payload() -> dict:
    return request.get_json(silent=True) or {}


def register_routes(app):
    @app.before_request
    def _start_timer():
        request._started_at = time.perf_counter()

    @app.after_request
    def _log_request(response):
        duration_ms = round((time.perf_counter() - request._started_at) * 1000, 2)
        current_app.logger.info(
            json.dumps(
                {
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
        )
        return response

    @app.errorhandler(ValidationError)
    def _handle_validation_error(exc):
        return jsonify({"error": str(exc)}), 400

    @app.errorhandler(IntegrityError)
    def _handle_integrity_error(exc):
        db.session.rollback()
        current_app.logger.warning("Database integrity error", exc_info=exc)
        return jsonify({"error": "Duplicate or invalid database value"}), 409

    @app.errorhandler(404)
    def _handle_not_found(exc):
        return jsonify({"error": "Not found"}), 404

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            app_name=current_app.config["APP_NAME"],
            app_env=current_app.config["APP_ENV"],
            version=current_app.config["APP_VERSION"],
        )

    @app.get("/healthz")
    def healthz():
        return jsonify(
            {
                "status": "ok",
                "service": current_app.config["APP_NAME"],
                "version": current_app.config["APP_VERSION"],
                "environment": current_app.config["APP_ENV"],
            }
        )

    @app.get("/readyz")
    def readyz():
        checks = {"database": "ok", "cache": "disabled"}
        db.session.execute(text("SELECT 1"))
        redis_client = current_app.extensions.get("redis_client")
        if redis_client:
            redis_client.ping()
            checks["cache"] = "ok"
        return jsonify({"status": "ready", "checks": checks})

    @app.get("/metrics")
    def metrics():
        car_counts = (
            db.session.query(Car.status, func.count(Car.id)).group_by(Car.status).all()
        )
        rental_counts = (
            db.session.query(Rental.status, func.count(Rental.id))
            .group_by(Rental.status)
            .all()
        )
        lines = [
            "# HELP car_rental_cars_total Number of cars by status",
            "# TYPE car_rental_cars_total gauge",
        ]
        lines.extend(
            f'car_rental_cars_total{{status="{status}"}} {count}'
            for status, count in car_counts
        )
        lines.extend(
            [
                "# HELP car_rental_rentals_total Number of rentals by status",
                "# TYPE car_rental_rentals_total gauge",
            ]
        )
        lines.extend(
            f'car_rental_rentals_total{{status="{status}"}} {count}'
            for status, count in rental_counts
        )
        return Response("\n".join(lines) + "\n", mimetype="text/plain")

    @app.get("/api/cars")
    def list_cars():
        status = request.args.get("status")
        cache_key = f"cars:list:{status or 'all'}"
        cached = cache_get_json(cache_key)
        if cached:
            return jsonify(cached)

        query = Car.query.order_by(Car.id.asc())
        if status:
            query = query.filter(Car.status == status)
        payload = {"items": [car.to_dict() for car in query.all()]}
        cache_set_json(cache_key, payload)
        return jsonify(payload)

    @app.post("/api/cars")
    def add_car():
        car = create_car(_json_payload())
        cache_delete("cars:list:all")
        cache_delete(f"cars:list:{car.status}")
        return jsonify(car.to_dict()), 201

    @app.patch("/api/cars/<int:car_id>/status")
    def set_car_status(car_id):
        car = update_car_status(car_id, _json_payload().get("status", ""))
        cache_delete("cars:list:all")
        cache_delete("cars:list:available")
        cache_delete("cars:list:rented")
        cache_delete("cars:list:maintenance")
        return jsonify(car.to_dict())

    @app.get("/api/customers")
    def list_customers():
        customers = Customer.query.order_by(Customer.id.asc()).all()
        return jsonify({"items": [customer.to_dict() for customer in customers]})

    @app.post("/api/customers")
    def add_customer():
        customer = create_customer(_json_payload())
        return jsonify(customer.to_dict()), 201

    @app.get("/api/rentals")
    def list_rentals():
        status = request.args.get("status")
        query = Rental.query.order_by(Rental.created_at.desc())
        if status:
            query = query.filter(Rental.status == status)
        return jsonify({"items": [rental.to_dict() for rental in query.all()]})

    @app.post("/api/rentals")
    def add_rental():
        rental = create_rental(_json_payload())
        cache_delete("cars:list:all")
        cache_delete("cars:list:available")
        cache_delete("cars:list:rented")
        return jsonify(rental.to_dict()), 201

    @app.post("/api/rentals/<int:rental_id>/return")
    def return_rental(rental_id):
        rental = complete_rental(rental_id)
        cache_delete("cars:list:all")
        cache_delete("cars:list:available")
        cache_delete("cars:list:rented")
        return jsonify(rental.to_dict())
