from typing import Any, Callable, TypeVar
from ..types import MiddlewareFunction

T = TypeVar('T', bound=Callable[..., Any])

def middleware(handler: MiddlewareFunction) -> Callable[[T], T]:
    """Decorator to define middleware for a route (method) or an API class."""

    def decorator(target: T) -> T:
        if isinstance(target, type):
            if not hasattr(target, "_middlewares"):
                setattr(target, "_middlewares", [])
            getattr(target, "_middlewares").append(handler)
        else:
            if not hasattr(target, "_middlewares"):
                setattr(target, '_middlewares', [])
            middlewares = getattr(target, '_middlewares')
            middlewares.append(handler)
        return target

    return decorator
