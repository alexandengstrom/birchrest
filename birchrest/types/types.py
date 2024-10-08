from typing import Callable
from ..http import Request, Response

NextFunction = Callable[[], None]

MiddlewareFunction = Callable[[Request, Response, NextFunction], None]

RouteHandler = Callable[[Request, Response], None]
