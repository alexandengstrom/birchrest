# type: ignore

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import time
from colorama import Fore, Style
from birchrest.middlewares import Logger


class TestLoggerMiddleware(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for the Logger middleware class.
    """

    async def asyncSetUp(self):
        """Set up the test environment before each test."""
        self.logger_middleware = Logger()

        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.clean_path = "/test"
        self.mock_request.client_address = "127.0.0.1"
        self.mock_request.correlation_id = "abc123"

        self.mock_response = MagicMock()
        self.mock_response._status_code = 200

        self.mock_next = AsyncMock()

    @patch('time.time', side_effect=[1000, 1001])
    @patch('logging.Logger.info')
    async def test_logger_middleware_logs_request_and_response(self, mock_log_info, mock_time):
        """
        Test that Logger middleware logs the request and response correctly.
        """

        await self.logger_middleware(self.mock_request, self.mock_response, self.mock_next)

        self.mock_next.assert_called_once()

        mock_log_info.assert_any_call(
            f"{Fore.GREEN}{Style.BRIGHT}Incoming Request: "
            f"{Style.RESET_ALL}Method={Fore.YELLOW}GET{Style.RESET_ALL}, "
            f"Path={Fore.YELLOW}/test{Style.RESET_ALL}, "
            f"Client={Fore.CYAN}127.0.0.1{Style.RESET_ALL}, "
            f"CorrelationID={Fore.MAGENTA}abc123{Style.RESET_ALL}"
        )

        mock_log_info.assert_any_call(
            f"{Fore.BLUE}{Style.BRIGHT}Outgoing Response: "
            f"{Style.RESET_ALL}Status={Fore.GREEN}200{Style.RESET_ALL}, "
            f"Client={Fore.CYAN}127.0.0.1{Style.RESET_ALL}, "
            f"CorrelationID={Fore.MAGENTA}abc123{Style.RESET_ALL}, "
            f"TimeTaken={Fore.YELLOW}1000.00ms{Style.RESET_ALL}"
        )

    @patch('time.time', side_effect=[1000, 1002])
    @patch('logging.Logger.info')
    async def test_logger_middleware_logs_error_response(self, mock_log_info, mock_time):
        """
        Test that Logger middleware logs the response correctly for error responses.
        """
        self.mock_response._status_code = 500

        await self.logger_middleware(self.mock_request, self.mock_response, self.mock_next)
        self.mock_next.assert_called_once()

        mock_log_info.assert_any_call(
            f"{Fore.BLUE}{Style.BRIGHT}Outgoing Response: "
            f"{Style.RESET_ALL}Status={Fore.RED}500{Style.RESET_ALL}, "
            f"Client={Fore.CYAN}127.0.0.1{Style.RESET_ALL}, "
            f"CorrelationID={Fore.MAGENTA}abc123{Style.RESET_ALL}, "
            f"TimeTaken={Fore.YELLOW}2000.00ms{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    unittest.main()
