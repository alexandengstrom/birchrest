def get(sub_route=""):
    """Decorator to define a GET route inside an API class."""
    def decorator(func):
        func._http_method = 'GET'
        func._sub_route = sub_route
        return func
    return decorator
