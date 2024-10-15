from typing import Callable, Any, cast
from functools import wraps
from ..types import FuncType


def produces(model: Any) -> Callable[[FuncType], FuncType]:
    """Decorator to attach a model for return type of a route"""

    def decorator(func: FuncType) -> FuncType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "_produces", model)

        return cast(FuncType, wrapper)

    return decorator
