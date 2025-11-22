from functools import wraps
from cachetools import TTLCache

# 1. 全局缓存池 (底层就是一个增强版 Dict)
# maxsize=1000: 最多存1000个key
# ttl=600: 存活600秒
_CACHE_STORE = TTLCache(maxsize=1000, ttl=600)


class CacheUtil:
    """手动管理缓存工具类"""

    @staticmethod
    def set(key: str, value: any):
        """插入/更新"""
        _CACHE_STORE[key] = value

    @staticmethod
    def get(key: str):
        """获取 (过期会自动返回 None)"""
        # 这里也可以用 _CACHE_STORE.get(key)
        if key in _CACHE_STORE:
            return _CACHE_STORE[key]
        return None

    @staticmethod
    def delete(key: str):
        """删除"""
        if key in _CACHE_STORE:
            del _CACHE_STORE[key]

    @staticmethod
    def clear():
        """清空所有"""
        _CACHE_STORE.clear()


# 2. 装饰器 (用于自动缓存函数结果)
def cached(ttl: int = 600):
    # 如果需要针对不同 ttl 创建不同池，可以在这里动态创建
    # 简单场景直接复用全局池即可，或者新建临时池
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成唯一Key
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if key in _CACHE_STORE:
                return _CACHE_STORE[key]

            result = await func(*args, **kwargs)
            _CACHE_STORE[key] = result
            return result

        return wrapper

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
