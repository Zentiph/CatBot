"""
internal.py
Internal constants and functions for CatBot.
"""

import logging

from discord import Color


LOG_FILE = "logs.log"
DEFAULT_EMBED_COLOR = Color(int("575afa", 16))


def get_token(*, override: str = ".env") -> str:
    """
    Get CatBot's token.

    :param override: Override file to provide a different token, defaults to ".env"
    :type override: str
    :return: CatBot token
    :rtype: str
    """

    with open(override, encoding="utf8") as file:
        line = file.readline()
        while not line.startswith("TOKEN="):
            line = file.readline()
        index = line.find("=")

    return line[index + 1 :].strip().strip('"')


def generate_ansi(r: int, g: int, b: int) -> str:
    """
    Generate an ANSI code given the RGB color.

    :param r: R value
    :type r: int
    :param g: G value
    :type g: int
    :param b: B value
    :type b: int
    :return: ANSI code matching the RGB color
    :rtype: str
    """

    return f"\x1b[38;2;{r};{g};{b}m"


class ColorFormatter(logging.Formatter):
    """
    Custom color formatter for logging stream outputs.
    """

    BOLD = "\x1b[1m"
    DEBUG = generate_ansi(166, 227, 161)
    INFO = generate_ansi(93, 157, 243)
    WARNING = generate_ansi(255, 255, 0)
    ERROR = generate_ansi(255, 0, 0)
    FATAL = generate_ansi(255, 0, 0) + BOLD
    RESET = "\x1b[0m"
    FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: DEBUG + FORMAT + RESET,
        logging.INFO: INFO + FORMAT + RESET,
        logging.WARNING: WARNING + FORMAT + RESET,
        logging.ERROR: ERROR + FORMAT + RESET,
        logging.CRITICAL: FATAL + FORMAT + RESET,
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
