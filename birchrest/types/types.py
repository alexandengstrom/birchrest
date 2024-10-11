from typing import Callable, TypeVar, Any, Awaitable
from ..http import Request, Response

# NextFunction is now expected to return an Awaitable (async function)
NextFunction = Callable[[], Awaitable[None]]

# MiddlewareFunction is now async and returns an Awaitable
MiddlewareFunction = Callable[[Request, Response, NextFunction], Awaitable[None]]

# AuthHandlerFunction is async and returns an Awaitable
AuthHandlerFunction = Callable[[Request, Response], Awaitable[Any]]

# RouteHandler is async and returns an Awaitable
RouteHandler = Callable[[Request, Response], Awaitable[None]]

# FuncType remains a generic callable, but now we assume it's async
FuncType = TypeVar("FuncType", bound=Callable[..., Awaitable[Any]])

# ErrorHandler is async and returns an Awaitable
ErrorHandler = Callable[[Request, Response, Exception], Awaitable[None]]
