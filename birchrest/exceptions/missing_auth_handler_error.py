class MissingAuthHandlerError(Exception):
    """Exception raised when a protected route is used without an authentication handler."""

    def __init__(self) -> None:
        message = (
            "Missing authentication handler: In order to use the `protected` decorator, "
            "you must register a global authentication handler with the main application."
        )
        super().__init__(message)
