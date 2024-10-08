def params(model):
    def decorator(func):
        func._validate_params = model
        return func
    return decorator
