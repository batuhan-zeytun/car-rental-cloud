from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, UniqueConstraint

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Car(TimestampMixin, db.Model):
    __tablename__ = "cars"
    __table_args__ = (
        CheckConstraint(
            "status in ('available', 'rented', 'maintenance')",
            name="cars_status_check",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(24), unique=True, nullable=False, index=True)
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    daily_rate = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(24), default="available", nullable=False, index=True)

    rentals = db.relationship("Rental", back_populates="car")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "location": self.location,
            "daily_rate": float(self.daily_rate),
            "status": self.status,
        }


class Customer(TimestampMixin, db.Model):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("email", name="customers_email_unique"),
    )

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False, index=True)
    phone = db.Column(db.String(32), nullable=False)

    rentals = db.relationship("Rental", back_populates="customer")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
        }


class Rental(TimestampMixin, db.Model):
    __tablename__ = "rentals"
    __table_args__ = (
        CheckConstraint(
            "status in ('active', 'completed', 'cancelled')",
            name="rentals_status_check",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False, index=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(24), default="active", nullable=False, index=True)

    car = db.relationship("Car", back_populates="rentals")
    customer = db.relationship("Customer", back_populates="rentals")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "car": self.car.to_dict() if self.car else None,
            "customer": self.customer.to_dict() if self.customer else None,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "days": (self.end_date - self.start_date).days + 1,
            "total_price": float(Decimal(self.total_price)),
            "status": self.status,
        }
