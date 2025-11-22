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
    def get(key: str):
        with CacheUtil._lock:
            if key in _CACHE_STORE:
                return _CACHE_STORE[key]
            return None

    @staticmethod
    def delete(key: str):
        with CacheUtil._lock:
            if key in _CACHE_STORE:
                del _CACHE_STORE[key]

    @staticmethod
    def clear():
        with CacheUtil._lock:
            _CACHE_STORE.clear()


def cached(ttl: int = 600):
    """Cache decorator supporting both sync and async functions"""

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                with CacheUtil._lock:
                    if key in _CACHE_STORE:
                        return _CACHE_STORE[key]

                result = await func(*args, **kwargs)

                with CacheUtil._lock:
                    _CACHE_STORE[key] = result
                return result

            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                with CacheUtil._lock:
                    if key in _CACHE_STORE:
                        return _CACHE_STORE[key]

                result = func(*args, **kwargs)

                with CacheUtil._lock:
                    _CACHE_STORE[key] = result
                return result

            return sync_wrapper

    return decorator


cache_util = CacheUtil()
