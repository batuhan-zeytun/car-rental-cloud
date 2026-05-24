import json

from flask import current_app


def get_redis():
    return current_app.extensions.get("redis_client")


def cache_get_json(key: str):
    redis_client = get_redis()
    if not redis_client:
        return None
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except Exception:
        current_app.logger.warning("Cache read failed", exc_info=True)
        return None


def cache_set_json(key: str, value, ttl_seconds: int | None = None) -> None:
    redis_client = get_redis()
    if not redis_client:
        return
    ttl = ttl_seconds or current_app.config["CACHE_TTL_SECONDS"]
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception:
        current_app.logger.warning("Cache write failed", exc_info=True)


def cache_delete(key: str) -> None:
    redis_client = get_redis()
    if redis_client:
        try:
            redis_client.delete(key)
        except Exception:
            current_app.logger.warning("Cache delete failed", exc_info=True)
