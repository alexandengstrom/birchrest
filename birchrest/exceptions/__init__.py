"""
This module defines custom exceptions used throughout the BirchRest framework.

Exceptions:
- **InvalidControllerRegistration**: Raised when a controller that does not inherit from the `Controller` base class is registered.
- **MissingAuthHandlerError**: Raised when an authentication handler is required but has not been provided.
- **ApiError**: Represents errors related to API requests, such as 404 Not Found or 500 Internal Server Error, with customizable status codes and messages.

These exceptions are used to manage error handling and enforce proper application behavior.

Exported exceptions:
- `InvalidControllerRegistration`
- `MissingAuthHandlerError`
- `ApiError`
"""

from .invalid_controller_registration import InvalidControllerRegistration
from .missing_auth_handler_error import MissingAuthHandlerError
from .api_error import ApiError

__all__ = ["InvalidControllerRegistration", "MissingAuthHandlerError", "ApiError"]