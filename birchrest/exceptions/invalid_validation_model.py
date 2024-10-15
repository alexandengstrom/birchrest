from typing import Type, Any


class InvalidValidationModel(TypeError):
    """
    Exception raised when the provided class is not a valid dataclass.

    This error occurs when the user tries to use the validation decorators
    with a non-dataclass type. The error message will guide the user on how
    to resolve the issue by passing a proper dataclass to the validation decorators.
    """

    def __init__(self, invalid_class: Type[Any]):
        self.invalid_class = invalid_class
        identifier = getattr(invalid_class, "__name__", invalid_class)
        message = (
            f"Invalid model '{identifier}' provided. "
            "When using validation decorators, you must pass a dataclass as an argument. "
            "Ensure that the model you are passing is a valid dataclass."
        )
        super().__init__(message)
