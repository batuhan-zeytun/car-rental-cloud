from .extensions import db
from .models import Car, Customer


def seed_sample_data() -> None:
    if Car.query.count() > 0 or Customer.query.count() > 0:
        return

    cars = [
        Car(
            plate_number="06-AYBU-01",
            make="Toyota",
            model="Corolla Hybrid",
            year=2024,
            location="Ankara Esenboga Airport",
            daily_rate=1850,
        ),
        Car(
            plate_number="34-CRS-2026",
            make="Renault",
            model="Clio",
            year=2023,
            location="Istanbul Sabiha Gokcen",
            daily_rate=1250,
        ),
        Car(
            plate_number="35-CLOUD-7",
            make="Hyundai",
            model="Tucson",
            year=2024,
            location="Izmir Adnan Menderes",
            daily_rate=2450,
        ),
    ]
    customers = [
        Customer(
            full_name="Aybu Demo User",
            email="demo@aybu.edu.tr",
            phone="+90 312 000 0000",
        )
    ]
    db.session.add_all(cars + customers)
    db.session.commit()
