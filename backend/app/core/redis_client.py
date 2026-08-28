import json
import logging
from typing import Optional, Any, Dict
from app.core.config import settings

logger = logging.getLogger("finance_controller")

class RedisCacheManager:
    """
    Enterprise Redis cache client with automatic in-memory RAM fallback.
    """
    def __init__(self):
        self._redis = None
        self._is_connected = False
        self._memory_cache: Dict[str, Any] = {}

        if settings.REDIS_ENABLED:
            self._connect()

    def _connect(self):
        try:
            import redis
            self._redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0
            )
            # Test ping
            self._redis.ping()
            self._is_connected = True
            logger.info(f"✅ [REDIS CONNECTED] Connected to Redis at {settings.REDIS_URL}")
        except Exception as e:
            self._is_connected = False
            self._redis = None
            logger.info(f"ℹ️ [REDIS OFFLINE] Redis not reachable ({str(e)}). Using high-speed in-memory Python RAM cache fallback.")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieves and deserializes JSON from Redis or fallback memory cache."""
        if self._is_connected and self._redis:
            try:
                raw = self._redis.get(key)
                if raw:
                    return json.loads(raw)
                return None
            except Exception as e:
                logger.warning(f"Redis get error on key '{key}': {e}. Falling back to memory.")
        
        # In-memory fallback
        return self._memory_cache.get(key)

    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool:
        """Serializes and saves JSON to Redis with TTL, or saves to fallback memory cache."""
        ttl = ttl_seconds if ttl_seconds is not None else settings.REDIS_TTL_SECONDS
        json_str = json.dumps(value)

        if self._is_connected and self._redis:
            try:
                self._redis.setex(key, ttl, json_str)
                return True
            except Exception as e:
                logger.warning(f"Redis set error on key '{key}': {e}. Falling back to memory.")

        # In-memory fallback
        self._memory_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        """Deletes a key from Redis and fallback memory cache."""
        if self._is_connected and self._redis:
            try:
                self._redis.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error on key '{key}': {e}")

        self._memory_cache.pop(key, None)
        return True

    def flush_pattern(self, pattern: str = "schema:*") -> int:
        """Deletes all keys matching a pattern from Redis and memory cache."""
        deleted_count = 0
        if self._is_connected and self._redis:
            try:
                keys = self._redis.keys(pattern)
                if keys:
                    deleted_count = self._redis.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis flush error on pattern '{pattern}': {e}")

        # Clear matching from in-memory cache
        mem_keys = [k for k in self._memory_cache.keys() if k.startswith(pattern.replace("*", ""))]
        for mk in mem_keys:
            self._memory_cache.pop(mk, None)
            deleted_count += 1

        return deleted_count

# Global singleton
redis_client = RedisCacheManager()
