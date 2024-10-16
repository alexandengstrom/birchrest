from typing import Callable, Any, cast
from functools import wraps
from ..types import FuncType


def protected() -> Callable[[FuncType], FuncType]:
    """Decorator to mark a route as protected inside an API class."""

    def decorator(func: FuncType) -> FuncType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "_is_protected", True)

        return cast(FuncType, wrapper)

    return decorator
