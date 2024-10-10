from typing import Callable, Any, cast
from functools import wraps
from ..types import FuncType


def body(model: Any) -> Callable[[FuncType], FuncType]:
    """Decorator to attach a model for body validation to a function."""

    def decorator(func: FuncType) -> FuncType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "_validate_body", model)

        return cast(FuncType, wrapper)

    return decorator
