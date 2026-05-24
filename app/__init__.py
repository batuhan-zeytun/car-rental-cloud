import json
import logging
import sys

import click
from flask import Flask

from .config import Config
from .extensions import db
from .routes import register_routes
from .seed import seed_sample_data


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(app: Flask) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    app.logger.handlers = [handler]
    app.logger.setLevel(app.config["LOG_LEVEL"])


def init_redis(app: Flask) -> None:
    app.extensions["redis_client"] = None
    redis_url = app.config.get("REDIS_URL")
    if not redis_url:
        return

    try:
        import redis

        app.extensions["redis_client"] = redis.from_url(
            redis_url, decode_responses=True, socket_timeout=1
        )
        app.extensions["redis_client"].ping()
        app.logger.info("Redis cache connected")
    except Exception:
        app.logger.warning("Redis cache unavailable", exc_info=True)
        app.extensions["redis_client"] = None


def create_app(config_object=Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    configure_logging(app)
    db.init_app(app)
    init_redis(app)
    register_routes(app)

    if app.config.get("AUTO_CREATE_DB", True):
        with app.app_context():
            db.create_all()
            if app.config.get("SEED_SAMPLE_DATA", True):
                seed_sample_data()

    register_commands(app)
    return app


def register_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with sample cars and customers."""
        seed_sample_data()
        click.echo("Sample data seeded.")

    @app.cli.command("drop-db")
    @click.confirmation_option(prompt="This will delete all data. Are you sure?")
    def drop_db():
        """Drop all database tables."""
        db.drop_all()
        click.echo("All tables dropped.")

    @app.cli.command("stats")
    def stats():
        """Print current fleet and rental statistics."""
        from .models import Car, Rental
        from sqlalchemy import func

        car_counts = db.session.query(Car.status, func.count(Car.id)).group_by(Car.status).all()
        rental_counts = db.session.query(Rental.status, func.count(Rental.id)).group_by(Rental.status).all()

        click.echo("\n── Fleet stats ──────────────────")
        for status, count in car_counts:
            click.echo(f"  {status:<14} {count}")
        click.echo("\n── Rental stats ─────────────────")
        for status, count in rental_counts:
            click.echo(f"  {status:<14} {count}")
        click.echo("")
