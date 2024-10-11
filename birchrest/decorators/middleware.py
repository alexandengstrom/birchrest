from typing import Any
from ..types import MiddlewareFunction

def middleware(handler: MiddlewareFunction) -> Any:
    """Decorator to define middleware for a route (method) or an API class."""

    def decorator(target: Any) -> Any:
        if isinstance(target, type):
            if not hasattr(target, "_middlewares"):
                setattr(target, "_middlewares", [])
                # target._middlewares = []
            getattr(target, "_middlewares").append(handler)
            # target._middlewares.append(handler)
            return target
        else:
            if not hasattr(target, "_middlewares"):
                target._middlewares = []
            target._middlewares.append(handler)
            return target

    return decorator
