from ..http import Request, Response
from typing import Callable, TypeVar, Any, cast
from functools import wraps


NextFunction = Callable[[], None]

MiddlewareFunction = Callable[[Request, Response, NextFunction], None]

AuthHandlerFunction = Callable[[Request, Response], None]

RouteHandler = Callable[[Request, Response], None]

FuncType = TypeVar('FuncType', bound=Callable[..., Any])
