import time
from collections import defaultdict
from typing import Dict, Any
from ..http import Request
from ..http import Response
from ..types import NextFunction
from .middleware import Middleware


class RateLimiter(Middleware):
    """
    A rate-limiting middleware that limits the number of requests per
    client (IP or token) within a specified time window.
    """

    def __init__(self, max_requests: int = 2, window_seconds: int = 10) -> None:
        """
        :param max_requests: Maximum number of requests allowed within the time window
        :param window_seconds: The time window in seconds during which
        max_requests applies
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_log: Dict[str, Any] = defaultdict(
            lambda: {"timestamps": [], "request_count": 0}
        )

    def _clean_old_requests(self, client_id: str) -> None:
        """
        Remove requests older than the current time window for a given client.
        """
        current_time = time.time()
        client_log = self.request_log[client_id]
        client_log["timestamps"] = [
            timestamp
            for timestamp in client_log["timestamps"]
            if current_time - timestamp <= self.window_seconds
        ]
        client_log["request_count"] = len(client_log["timestamps"])

    async def __call__(self, req: Request, res: Response, _next: NextFunction) -> None:
        """
        Middleware to handle rate limiting for each incoming request.
        :param req: The HTTP request object
        :param res: The HTTP response object
        :param next: The next middleware or handler to call
        """

        client_id = req.client_address

        self._clean_old_requests(client_id)

        if self.request_log[client_id]["request_count"] >= self.max_requests:
            res.status(429).send({"error": "Too Many Requests"})
            return

        self.request_log[client_id]["timestamps"].append(time.time())
        self.request_log[client_id]["request_count"] += 1
        await _next()
