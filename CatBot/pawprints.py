"""Logging utility for CatBot."""

__author__ = "Gavin Borne"
__license__ = "MIT"

import logging
from enum import StrEnum

LOG_FILE = "logs.log"
"""The file to log to."""
LOGGING_CHANNEL = 1306045987319451718
"""The channel to post command logs in.
This is a temporary solution until a DB is added.
"""
DEFAULT_FMT = (
    "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s (%(filename)s:%(lineno)d)"
)
"""The default logging format to use."""
DEFAULT_DATE_FMT = "%Y-%m-%d %H:%M:%S"
"""The default logging date format to use."""


class AnsiColor(StrEnum):
    """An enum containing all ANSI color codes for logging colors."""

    DEBUG = "\x1b[32m"  # green
    INFO = "\x1b[34m"  # blue
    WARNING = "\x1b[33m"  # yellow
    ERROR = "\x1b[31m"  # red
    CRITICAL = "\x1b[31m\x1b[1m"  # red in bold
    RESET = "\x1b[0m"


class AnsiColorFormatter(logging.Formatter):
    """A formatter that colors logs based on their level using ANSI color codes."""

    def _format_by_level(self, fmt: str, level: int, /) -> str:
        match level:
            case logging.DEBUG:
                return AnsiColor.DEBUG + fmt + AnsiColor.RESET
            case logging.INFO:
                return AnsiColor.INFO + fmt + AnsiColor.RESET
            case logging.WARN:
                return AnsiColor.WARNING + fmt + AnsiColor.RESET
            case logging.ERROR:
                return AnsiColor.ERROR + fmt + AnsiColor.RESET
            case logging.CRITICAL:
                return AnsiColor.CRITICAL + fmt + AnsiColor.RESET
            case _:
                return fmt

    def format(self, record: logging.LogRecord) -> str:
        return self._format_by_level(super().format(record), record.levelno)


def config_logging(
    logfile: str,
    *,
    console_logging: bool,
    colored_logs: bool,
    debug: bool,
    fmt: str = DEFAULT_FMT,
    date_fmt: str = DEFAULT_DATE_FMT,
) -> None:
    """Configure CatBot's logging.

    Args:
        logfile (str): The file to log to.
        console_logging (bool): Whether to enable console logging.
        colored_logs (bool): Whether to color console logs.
        debug (bool): Whether to log debug messages.
        fmt (str, optional): The logging format to use. Defaults to DEFAULT_FMT.
        date_fmt (str, optional): The logging date format to use.
            Defaults to DEFAULT_DATE_FMT.
    """

    handlers: list[logging.Handler] = []
    if console_logging:
        stream_handler = logging.StreamHandler()
        handlers.append(stream_handler)

        if colored_logs:
            stream_handler.setFormatter(AnsiColorFormatter())

    handlers.append(logging.FileHandler(logfile, encoding="utf-8"))

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, handlers=handlers, format=fmt, datefmt=date_fmt)

    logging.info(
        f"CatBot logging config: logfile={logfile}, debug={debug},"
        f"no-console-logging={not console_logging}, colored-logs={colored_logs}"
    )
