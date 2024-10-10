"""
Contains more complicated types that are used in the project.
"""

from typing import Callable, TypeVar, Any
from ..http import Request, Response


NextFunction = Callable[[], None]

MiddlewareFunction = Callable[[Request, Response, NextFunction], None]

AuthHandlerFunction = Callable[[Request, Response], None]

RouteHandler = Callable[[Request, Response], None]

FuncType = TypeVar("FuncType", bound=Callable[..., Any])

ErrorHandler = Callable[[Request, Response, Exception], None]
