import threading
import inspect
from functools import wraps
from typing import Any

from cachetools import TTLCache

# 全局缓存池
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
    """
    智能缓存装饰器：自动支持 Sync 和 Async 函数
    """

    def decorator(func):
        # 1. 判断被装饰函数是否是异步函数
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 生成 Key
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                # 读缓存
                with CacheUtil._lock:
                    if key in _CACHE_STORE:
                        return _CACHE_STORE[key]

                # 执行原函数 (Await)
                result = await func(*args, **kwargs)

                # 写缓存
                with CacheUtil._lock:
                    _CACHE_STORE[key] = result
                return result

            return async_wrapper

        else:
            # 2. 同步函数的 Wrapper (Service 层专用)
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                with CacheUtil._lock:
                    if key in _CACHE_STORE:
                        return _CACHE_STORE[key]

                # 执行原函数 (直接调用)
                result = func(*args, **kwargs)

                with CacheUtil._lock:
                    _CACHE_STORE[key] = result
                return result

            return sync_wrapper

    return decorator


# 导出实例
cache_util = CacheUtil()

# 示例用法:
# 方式1：手动 CRUD
# cache_util.set("user:1", {"name": "Jack"})
# user = cache_util.get("user:1")
# cache_util.delete("user:1")
#
# # 方式2：装饰器 (自动挡)
# @cached(ttl=300)
# async def get_heavy_data(param):
#     return await db.query(...)
