from typing import Callable, TypeVar, Any, cast
from functools import wraps
from ..types import FuncType


def head(sub_route: str = "") -> Callable[[FuncType], FuncType]:
    """Decorator to define a HEAD route inside an API class."""

    def decorator(func: FuncType) -> FuncType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "_http_method", "HEAD")
        setattr(wrapper, "_sub_route", sub_route)

        return cast(FuncType, wrapper)

    return decorator