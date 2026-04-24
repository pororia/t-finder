from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[dict] = None

    @classmethod
    def ok(cls, data: T) -> "APIResponse[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, code: str, message: str) -> "APIResponse":
        return cls(success=False, data=None, error={"code": code, "message": message})
