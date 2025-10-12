from typing import Final

__author__: Final[str]
__license__: Final[str]

import logging
from enum import StrEnum

LOG_FILE: Final[str]
LOGGING_CHANNEL: Final[int]
DEFAULT_FMT: Final[str]
DEFAULT_DATE_FMT: Final[str]

class AnsiColor(StrEnum):
    DEBUG = "\x1b[32m"
    INFO = "\x1b[34m"
    WARNING = "\x1b[33m"
    ERROR = "\x1b[31m"
    CRITICAL = "\x1b[31m\x1b[1m"
    RESET = "\x1b[0m"

class AnsiColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str: ...

def config_logging(
    logfile: str,
    *,
    console_logging: bool,
    colored_logs: bool,
    debug: bool,
    fmt: str = DEFAULT_FMT,
    date_fmt: str = DEFAULT_DATE_FMT,
) -> None: ...
