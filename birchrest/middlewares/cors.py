from typing import List, Callable
from ..http import Request
from ..http import Response
from ..types import NextFunction


class Cors:
    def __init__(
        self,
        allow_origins: List[str] = ["*"],
        allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers: List[str] = ["Content-Type", "Authorization"],
        allow_credentials: bool = False,
        max_age: int = 86400
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

    def __call__(self, req: Request, res: Response, next: NextFunction) -> None:
        origin = req.get_header("Origin") or "*"

        if req.method == "OPTIONS":
            self._handle_preflight(origin, res)
        else:
            self._add_cors_headers(origin, res)
            next()

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