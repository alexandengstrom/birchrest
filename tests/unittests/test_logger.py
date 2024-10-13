# type: ignore

import unittest
from unittest.mock import patch
from colorama import Fore, Style
from birchrest.utils import Logger


class TestLogger(unittest.TestCase):
    """
    Unit tests for the custom Logger class.
    """

    @patch('builtins.print')
    @patch('os.getenv', return_value='debug')
    def test_debug_logging(self, mock_getenv, mock_print):
        """Test the debug logging with a message."""
        test_message = "This is a debug message"
        
        Logger.debug(test_message)

        mock_print.assert_called_once_with(
            unittest.mock.ANY
        )

    @patch('builtins.print')
    @patch('os.getenv', return_value='info')
    def test_info_logging_with_object(self, mock_getenv, mock_print):
        """Test the info logging with a message and an attached object."""
        test_message = "This is an info message"
        test_object = {"key": "value"}

        Logger.info(test_message, test_object)

        expected_log = (
            f"{Fore.GREEN}INFO: {test_message}{Style.RESET_ALL}\n"
            "{\n"
            '    "key": "value"\n'
            "}"
        )

        mock_print.assert_called_once_with(unittest.mock.ANY)

    @patch('builtins.print')
    @patch('os.getenv', return_value='warning')
    def test_warning_logging(self, mock_getenv, mock_print):
        """Test the warning logging with a message."""
        test_message = "This is a warning"

        Logger.warning(test_message)

        mock_print.assert_called_once_with(
            unittest.mock.ANY
        )

    @patch('builtins.print')
    @patch('os.getenv', return_value='error')
    def test_error_logging_with_invalid_object(self, mock_getenv, mock_print):
        """Test the error logging with an invalid JSON object."""
        test_message = "This is an error message"
        test_object = set([1, 2, 3])

        Logger.error(test_message, test_object)

        mock_print.assert_called_once_with(
            unittest.mock.ANY
        )

    @patch('builtins.print')
    @patch('os.getenv', return_value='info')
    def test_logging_below_threshold(self, mock_getenv, mock_print):
        """Test that logging below the set log level does not produce output."""

        Logger.debug("This is a debug message")
        mock_print.assert_not_called()

    @patch('builtins.print')
    @patch('os.getenv', return_value='debug')
    def test_logging_json_error(self, mock_getenv, mock_print):
        """Test that invalid JSON objects are logged as errors."""
        invalid_object = object()
        Logger.debug("This is a debug message", invalid_object)

        expected_log = "[Invalid JSON object: <object object at"
        printed_message = mock_print.call_args[0][0]
        self.assertIn(expected_log, printed_message)


if __name__ == "__main__":
    unittest.main()
