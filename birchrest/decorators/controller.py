def controller(base_path = ""):
    def class_decorator(cls):
        cls._base_path = base_path
        return cls
    return class_decorator
