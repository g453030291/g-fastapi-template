import threading
import inspect
from functools import wraps
from typing import Any

from cachetools import TTLCache

_CACHE_STORE = TTLCache(maxsize=1000, ttl=600)


class CacheUtil:
    _lock = threading.Lock()

    @staticmethod
    def set(key: str, value: Any):
        with CacheUtil._lock:
            _CACHE_STORE[key] = value

    @staticmethod
    def get(key: str) -> Any:
        with CacheUtil._lock:
            return _CACHE_STORE.get(key)

    @staticmethod
    def delete(key: str):
        with CacheUtil._lock:
            _CACHE_STORE.pop(key, None)

    @staticmethod
    def clear():
        with CacheUtil._lock:
            _CACHE_STORE.clear()


def cached(ttl: int = 600):
    _cache: TTLCache = TTLCache(maxsize=1000, ttl=ttl)
    _lock = threading.Lock()

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = f"{args}:{kwargs}"
                with _lock:
                    if key in _cache:
                        return _cache[key]
                result = await func(*args, **kwargs)
                with _lock:
                    _cache[key] = result
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = f"{args}:{kwargs}"
                with _lock:
                    if key in _cache:
                        return _cache[key]
                result = func(*args, **kwargs)
                with _lock:
                    _cache[key] = result
                return result
            return sync_wrapper

    return decorator


cache_util = CacheUtil()
