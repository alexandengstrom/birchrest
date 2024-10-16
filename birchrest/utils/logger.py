import json
import os
from datetime import datetime
from typing import Any, Optional
from colorama import Fore, Style, init

init(autoreset=True)


class Logger:
    @staticmethod
    def _log(level: str, message: str, color: str, obj: Optional[Any] = None) -> None:
        """
        Internal logging method to format and print the log message with color.

        Args:
            level (str): The level of the log (DEBUG, INFO, WARNING, ERROR).
            message (str): The log message.
            color (str): The color for the log level.
            obj (Optional[Any]): An optional object to be logged in JSON format.
        """
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{color}{time_stamp} - {level}: {message}{Style.RESET_ALL}"

        if obj is not None:
            try:
                json_obj = json.dumps(obj, indent=4, sort_keys=True)
                log_message += f"\n{json_obj}"
            except (TypeError, ValueError):
                log_message += f"\n[Invalid JSON object: {obj}]"

        print(log_message)

    @staticmethod
    def _should_log(level: str) -> bool:
        """
        Determine if the given log level should be logged based on the environment log level setting.
        """

        convert = {"debug": 4, "info": 3, "warning": 2, "error": 1, "test": 0}

        log_level = os.getenv("birchrest_log_level", "info").lower()

        if log_level not in convert:
            log_level = "info"

        return convert.get(log_level, -1) >= convert[level]

    @staticmethod
    def debug(message: str, obj: Optional[Any] = None) -> None:
        """Logs a debug message with blue color."""
        if not Logger._should_log("debug"):
            return

        Logger._log("DEBUG", message, Fore.BLUE, obj)

    @staticmethod
    def info(message: str, obj: Optional[Any] = None) -> None:
        """Logs an info message with green color."""
        if not Logger._should_log("info"):
            return

        Logger._log("INFO", message, Fore.GREEN, obj)

    @staticmethod
    def warning(message: str, obj: Optional[Any] = None) -> None:
        """Logs a warning message with yellow color."""
        if not Logger._should_log("warning"):
            return

        Logger._log("WARNING", message, Fore.YELLOW, obj)

    @staticmethod
    def error(message: str, obj: Optional[Any] = None) -> None:
        """Logs an error message with red color."""
        if not Logger._should_log("error"):
            return

        Logger._log("ERROR", message, Fore.RED, obj)
