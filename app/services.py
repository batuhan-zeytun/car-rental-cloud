from datetime import date
from decimal import Decimal

from sqlalchemy import and_

from .extensions import db
from .models import Car, Customer, Rental


class ValidationError(Exception):
    pass


def parse_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be an ISO date like 2026-05-22") from exc


def create_car(payload: dict) -> Car:
    required = ["plate_number", "make", "model", "year", "location", "daily_rate"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    status = str(payload.get("status", "available")).strip()
    if status not in {"available", "rented", "maintenance"}:
        raise ValidationError("status must be available, rented, or maintenance")

    try:
        year = int(payload["year"])
        daily_rate = Decimal(str(payload["daily_rate"]))
    except (TypeError, ValueError) as exc:
        raise ValidationError("year and daily_rate must be numeric") from exc
    if year < 2000 or daily_rate <= 0:
        raise ValidationError("year must be 2000 or newer and daily_rate must be positive")

    car = Car(
        plate_number=str(payload["plate_number"]).strip().upper(),
        make=str(payload["make"]).strip(),
        model=str(payload["model"]).strip(),
        year=year,
        location=str(payload["location"]).strip(),
        daily_rate=daily_rate,
        status=status,
    )
    db.session.add(car)
    db.session.commit()
    return car


def update_car_status(car_id: int, status: str) -> Car:
    if status not in {"available", "rented", "maintenance"}:
        raise ValidationError("status must be available, rented, or maintenance")
    car = db.session.get(Car, car_id)
    if not car:
        raise ValidationError("Car not found")
    car.status = status
    db.session.commit()
    return car


def create_customer(payload: dict) -> Customer:
    required = ["full_name", "email", "phone"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    customer = Customer(
        full_name=str(payload["full_name"]).strip(),
        email=str(payload["email"]).strip().lower(),
        phone=str(payload["phone"]).strip(),
    )
    db.session.add(customer)
    db.session.commit()
    return customer


def create_rental(payload: dict) -> Rental:
    required = ["car_id", "customer_id", "start_date", "end_date"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    car = db.session.get(Car, int(payload["car_id"]))
    customer = db.session.get(Customer, int(payload["customer_id"]))
    if not car:
        raise ValidationError("Car not found")
    if not customer:
        raise ValidationError("Customer not found")
    if car.status == "maintenance":
        raise ValidationError("Car is in maintenance")

    start_date = parse_date(payload["start_date"], "start_date")
    end_date = parse_date(payload["end_date"], "end_date")
    if end_date < start_date:
        raise ValidationError("end_date must be on or after start_date")

    overlapping = Rental.query.filter(
        Rental.car_id == car.id,
        Rental.status == "active",
        and_(Rental.start_date <= end_date, Rental.end_date >= start_date),
    ).first()
    if overlapping:
        raise ValidationError("Car is already rented for the selected dates")

    days = (end_date - start_date).days + 1
    total_price = Decimal(car.daily_rate) * Decimal(days)
    rental = Rental(
        car_id=car.id,
        customer_id=customer.id,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        status="active",
    )
    car.status = "rented"
    db.session.add(rental)
    db.session.commit()
    return rental


def complete_rental(rental_id: int) -> Rental:
    rental = db.session.get(Rental, rental_id)
    if not rental:
        raise ValidationError("Rental not found")
    if rental.status != "active":
        raise ValidationError("Only active rentals can be returned")

    rental.status = "completed"
    rental.car.status = "available"
    db.session.commit()
    return rental
