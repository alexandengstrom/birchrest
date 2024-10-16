from abc import ABC, abstractmethod

from ..http import Request, Response
from ..types import NextFunction


class Middleware(ABC):
    """
    Base class for all middlewares. All middlewares should inherit from this class.
    This class provides a unified interface to handle both synchronous and asynchronous middlewares.
    """

    @abstractmethod
    async def __call__(self, req: Request, res: Response, next: NextFunction) -> None:
        """
        This method should be overridden by user-defined middleware classes.
        It must be an asynchronous function.
        """
        raise NotImplementedError("Middleware must implement the __call__ method")
