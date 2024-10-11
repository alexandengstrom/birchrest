"""
This module serves as the main entry point for the BirchRest framework.

Modules imported include:
- `app`: Contains the core `BirchRest` class to handle application setup.
- `decorators`: Provides decorators like `get`, `post`, `controller`, and middleware helpers.
- `routes`: Defines controllers for managing routes.
- `http`: Handles HTTP requests, responses, and status codes.
- `types`: Defines core types such as middleware functions and route handlers.
- `exceptions`: Manages framework-specific errors and exceptions.
- `middlewares`: Includes various middleware like `RateLimiter`, `Logger`, and `Cors`.
- `unittest`: Includes the TestAdapter for unittesting.

"""

from .app import BirchRest
from .routes import Controller
from .middlewares import Middleware


__all__ = [
    "BirchRest",
    "Controller",
    "Middleware"
]