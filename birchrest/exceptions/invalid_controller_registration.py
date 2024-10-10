from typing import Any


class InvalidControllerRegistration(Exception):
    """Exception raised when an invalid class or instance is registered as a controller."""

    def __init__(self, received_object: Any) -> None:
        expected_class = "Controller"

        if isinstance(received_object, type):
            received_type = f"class '{received_object.__name__}'"
        else:
            received_type = f"instance of '{type(received_object).__name__}'"

        message = (
            f"Invalid registration: {received_type} cannot be registered as a controller. "
            f"Only subclasses of '{expected_class}' are allowed."
        )

        super().__init__(message)

        self.received_object = received_object
