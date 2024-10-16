from typing import Callable, Any, cast
from functools import wraps
from ..types import FuncType


def queries(model: Any) -> Callable[[FuncType], FuncType]:
    """Decorator to attach a model for query validation to a function."""

    def decorator(func: FuncType) -> FuncType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "_validate_queries", model)

        return cast(FuncType, wrapper)

    return decorator
