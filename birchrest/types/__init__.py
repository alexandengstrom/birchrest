"""
This module collects complex types used throughout the BirchRest framework to simplify and organize the code.

Types:
- **NextFunction**: Represents the next middleware function in the chain.
- **MiddlewareFunction**: Type for middleware functions that process requests and responses.
- **RouteHandler**: Defines a type for route handler functions.
- **AuthHandlerFunction**: Type for authentication handler functions.
- **FuncType**: Generic type for callable functions.
- **ErrorHandler**: Defines a type for error handling functions.

Exported types:
- `NextFunction`
- `MiddlewareFunction`
- `RouteHandler`
- `AuthHandlerFunction`
- `FuncType`
- `ErrorHandler`
"""


from .types import (
    NextFunction,
    MiddlewareFunction,
    RouteHandler,
    AuthHandlerFunction,
    FuncType,
    ErrorHandler,
)

__all__ = [
    "NextFunction",
    "MiddlewareFunction",
    "RouteHandler",
    "AuthHandlerFunction",
    "FuncType",
    "ErrorHandler",
]
