from typing import List
from ..http import Request
from ..http import Response
from ..types import NextFunction
from .middleware import Middleware


class Cors(Middleware):
    """
    Middleware for handling Cross-Origin Resource Sharing (CORS) in HTTP requests.

    This middleware ensures that the server can respond to cross-origin requests by
    controlling which origins, methods, and headers are allowed. It also handles
    preflight requests (OPTIONS method) for HTTP requests that require complex CORS
    handling, such as when using methods other than GET or POST or custom headers.

    The CORS settings, such as allowed origins, methods, and headers, can be configured
    when initializing the middleware. By default, it allows all origins, commonly used
    methods, and a few standard headers.

    Attributes:
        allow_origins (List[str]): List of allowed origins. Defaults to ["*"], allowing all origins.
        allow_methods (List[str]): List of allowed HTTP methods. Defaults to common methods like GET, POST, PUT, DELETE, etc.
        allow_headers (List[str]): List of allowed request headers. Defaults to ["Content-Type", "Authorization"].
        allow_credentials (bool): Whether or not to allow credentials (cookies, HTTP authentication, etc.). Defaults to False.
        max_age (int): How long the results of a preflight request can be cached (in seconds). Defaults to 86400 seconds (24 hours).

    Methods:
        __call__(req, res, next): Main entry point for the middleware. Adds the appropriate CORS headers to the response based on the request.
        _handle_preflight(origin, res): Handles preflight (OPTIONS) requests by responding with the appropriate CORS headers.
        _add_cors_headers(origin, res): Adds CORS headers to the response for non-OPTIONS requests.
        _is_origin_allowed(origin): Checks if the origin is allowed based on the allow_origins setting.
    """

    def __init__(
        self,
        allow_origins: List[str] = ["*"],
        allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers: List[str] = ["Content-Type", "Authorization"],
        allow_credentials: bool = False,
        max_age: int = 86400,
    ):
        """
        Initialize the CORS middleware.
        :param allow_origins: List of allowed origins. Default is ["*"] (all origins).
        :param allow_methods: List of allowed HTTP methods.
            Default includes common methods.
        :param allow_headers: List of allowed request headers.
            Default includes Content-Type and Authorization.
        :param allow_credentials: Whether or not to allow
            credentials. Default is False.
        :param max_age: How long the results of a preflight
            request can be cached, in seconds. Default is 86400 (24 hours).
        """
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    async def __call__(self, req: Request, res: Response, next: NextFunction) -> None:
        origin = req.get_header("Origin") or "*"

        if req.method == "OPTIONS":
            self._handle_preflight(origin, res)
        else:
            self._add_cors_headers(origin, res)
            await next()

    def _handle_preflight(self, origin: str, res: Response) -> None:
        """
        Handle preflight requests (OPTIONS method).
        """
        if self._is_origin_allowed(origin):
            res.set_header("Access-Control-Allow-Origin", origin)
        else:
            res.set_header("Access-Control-Allow-Origin", "*")

        res.set_header("Access-Control-Allow-Methods", ", ".join(self.allow_methods))
        res.set_header("Access-Control-Allow-Headers", ", ".join(self.allow_headers))
        res.set_header("Access-Control-Max-Age", str(self.max_age))

        if self.allow_credentials:
            res.set_header("Access-Control-Allow-Credentials", "true")

        res.status(204).send()

    def _add_cors_headers(self, origin: str, res: Response) -> None:
        """
        Add CORS headers to the response for non-OPTIONS requests.
        """
        if self._is_origin_allowed(origin):
            res.set_header("Access-Control-Allow-Origin", origin)
        else:
            res.set_header("Access-Control-Allow-Origin", "*")

        if self.allow_credentials:
            res.set_header("Access-Control-Allow-Credentials", "true")

    def _is_origin_allowed(self, origin: str) -> bool:
        """
        Check if the request origin is allowed.
        :param origin: The origin of the incoming request.
        :return: True if the origin is allowed, otherwise False.
        """
        return "*" in self.allow_origins or origin in self.allow_origins
