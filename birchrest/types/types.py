from typing import Callable, TypeVar, Any, Awaitable
from ..http import Request, Response

NextFunction = Callable[[], Awaitable[None]]

MiddlewareFunction = Callable[[Request, Response, NextFunction], Awaitable[None]]

AuthHandlerFunction = Callable[[Request, Response], Awaitable[Any]]

RouteHandler = Callable[[Request, Response], Awaitable[None]]

FuncType = TypeVar("FuncType", bound=Callable[..., Awaitable[Any]])

ErrorHandler = Callable[[Request, Response, Exception], Awaitable[None]]
