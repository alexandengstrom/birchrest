def protected():
    """Decorator to define a GET route inside an API class."""
    def decorator(target):
        target._is_protected = True
        return target
    return decorator
