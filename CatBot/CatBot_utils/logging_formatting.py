"""
logging_formatting.py
Logging formatting code.
"""

import logging

LOGGING_FORMAT = (
    "%(asctime)s | [%(levelname)s] %(name)s - %(message)s (%(filename)s:%(lineno)d)"
)


class ColorFormatter(logging.Formatter):
    """
    Custom color formatter for logging stream outputs.
    """

    DEBUG = "\x1b[38;2;166;227;161m"  # green
    INFO = "\x1b[38;2;93;157;243m"  # blue
    WARNING = "\x1b[38;2;255;255;0m"  # yellow
    ERROR = "\x1b[38;2;255;0;0m"  # red
    FATAL = "\x1b[38;2;255;0;0m" + "\x1b[1m"  # red in bold
    RESET = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: DEBUG + LOGGING_FORMAT + RESET,
        logging.INFO: INFO + LOGGING_FORMAT + RESET,
        logging.WARNING: WARNING + LOGGING_FORMAT + RESET,
        logging.ERROR: ERROR + LOGGING_FORMAT + RESET,
        logging.CRITICAL: FATAL + LOGGING_FORMAT + RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Apply the format to the log message.

        :param record: Logging record
        :type record: logging.LogRecord
        :return: Formatted log
        :rtype: str
        """

        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
