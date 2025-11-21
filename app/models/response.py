from typing import Generic, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: T | None = None

    @classmethod
    def success(cls, data: T = None, msg: str = "success"):
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def fail(cls, code: int = 400, msg: str = "error", data: Any = None):
        return cls(code=code, msg=msg, data=data)
