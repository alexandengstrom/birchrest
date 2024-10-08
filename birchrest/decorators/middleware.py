def middleware(handler):
    """Decorator to define middleware for a route (method) or an API class."""
    def decorator(target):
        if isinstance(target, type):
            if not hasattr(target, "_middlewares"):
                target._middlewares = []
            target._middlewares.append(handler)
            return target
        else:
            if not hasattr(target, "_middlewares"):
                target._middlewares = []
            target._middlewares.append(handler)
            return target
    return decorator
