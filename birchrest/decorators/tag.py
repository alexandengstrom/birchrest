from typing import Any, Callable, TypeVar

T = TypeVar('T', bound=Callable[..., Any])

def tag(*tags: str) -> Callable[[T], T]:
    """Decorator to define tags for a route (method) or an API class."""

    def decorator(target: T) -> T:
        if isinstance(target, type):
            if not hasattr(target, "_openapi_tags"):
                setattr(target, "_openapi_tags", [])
            getattr(target, "_openapi_tags").extend(tags)
        else:
            if not hasattr(target, "_openapi_tags"):
                setattr(target, '_openapi_tags', [])
            getattr(target, '_openapi_tags').extend(tags)
        return target

    return decorator
