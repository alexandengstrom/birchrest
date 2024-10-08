def post(sub_route=None):
    """Decorator to define a POST route inside an API class."""
    def decorator(func):
        func._http_method = 'POST'
        func._sub_route = sub_route
        return func
    return decorator