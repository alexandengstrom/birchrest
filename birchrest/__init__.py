"""
This module serves as the main entry point for the BirchRest framework.
It imports various components such as the core application class, decorators, 
HTTP request/response handling, route controllers, middleware, and exceptions 
needed to build and manage REST APIs.

Modules imported include:
- `app`: Contains the core `BirchRest` class to handle application setup.
- `decorators`: Provides decorators like `get`, `post`, `controller`, and middleware helpers.
- `routes`: Defines controllers for managing routes.
- `http`: Handles HTTP requests, responses, and status codes.
- `types`: Defines core types such as middleware functions and route handlers.
- `exceptions`: Manages framework-specific errors and exceptions.
- `middlewares`: Includes various middleware like `RateLimiter`, `Logger`, and `Cors`.

Additionally, this module exports all the necessary components for external use
via the `__all__` directive.
"""

from .app import BirchRest
from .decorators import (
    get,
    post,
    controller,
    middleware,
    protected,
    body,
    queries,
    params,
    patch,
    put,
    delete,
    options,
    head,
)
from .routes import Controller
from .http import Request, Response, HttpStatus, Server
from .types import (
    MiddlewareFunction,
    NextFunction,
    RouteHandler,
    AuthHandlerFunction,
    FuncType,
    ErrorHandler,
)
from .exceptions import InvalidControllerRegistration, MissingAuthHandlerError, ApiError
from .middlewares import RateLimiter, Logger, Cors
from .unittest import TestAdapter

__all__ = [
    "BirchRest",
    "Controller",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
    "protected",
    "body",
    "queries",
    "params",
    "controller",
    "middleware",
    "Request",
    "Response",
    "HttpStatus",
    "NextFunction",
    "MiddlewareFunction",
    "AuthHandlerFunction",
    "RouteHandler",
    "InvalidControllerRegistration",
    "MissingAuthHandlerError",
    "RateLimiter",
    "Logger",
    "Cors",
    "Server",
    "FuncType",
    "ApiError",
    "ErrorHandler",
    "TestAdapter",
]
