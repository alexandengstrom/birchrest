import time
import logging
from colorama import Fore, Style, init
from ..http import Request, Response
from ..types import NextFunction
from .middleware import Middleware

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("RequestLogger")


class Logger(Middleware):
    """
    Middleware to log incoming requests and outgoing responses with enhanced formatting and colors.
    Logs useful information including request method, path, client address, correlation ID, response status, and time taken.
    """

    async def __call__(self, req: Request, res: Response, next: NextFunction) -> None:
        """
        Middleware entry point.
        Logs the incoming request, processes the next middleware or handler,
        and logs the response with the time taken.

        :param req: The HTTP request object
        :param res: The HTTP response object
        :param next: The next middleware or handler to call
        """
        start_time = time.time()

        logger.info(
            f"{Fore.GREEN}{Style.BRIGHT}Incoming Request: "
            f"{Style.RESET_ALL}Method={Fore.YELLOW}{req.method}{Style.RESET_ALL}, "
            f"Path={Fore.YELLOW}{req.clean_path}{Style.RESET_ALL}, "
            f"Client={Fore.CYAN}{req.client_address}{Style.RESET_ALL}, "
            f"CorrelationID={Fore.MAGENTA}{req.correlation_id}{Style.RESET_ALL}"
        )

        await next()

        duration = (time.time() - start_time) * 1000

        status_color = Fore.GREEN if res._status_code < 400 else Fore.RED

        logger.info(
            f"{Fore.BLUE}{Style.BRIGHT}Outgoing Response: "
            f"{Style.RESET_ALL}Status={status_color}{res._status_code}{Style.RESET_ALL}, "
            f"Client={Fore.CYAN}{req.client_address}{Style.RESET_ALL}, "
            f"CorrelationID={Fore.MAGENTA}{req.correlation_id}{Style.RESET_ALL}, "
            f"TimeTaken={Fore.YELLOW}{duration:.2f}ms{Style.RESET_ALL}"
        )
