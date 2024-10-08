def queries(model):
    def decorator(func):
        func._validate_queries = model
        return func
    return decorator
