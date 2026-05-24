import json
import logging
import sys

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

    return app
