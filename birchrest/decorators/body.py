def body(model):
    def decorator(func):
        func._validate_body = model
        return func
    return decorator
