"""Logging utility for FizzBuzz."""

from enum import StrEnum
import logging

import discord
from discord.ext import commands

__author__ = "Gavin Borne"
__license__ = "MIT"

LOG_FILE = "logs.log"  # TODO: make an env var?
"""The file to log to."""


_DEFAULT_FMT = (
    "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s (%(filename)s:%(lineno)d)"
)
_DEFAULT_DATE_FMT = "%Y-%m-%d %H:%M:%S"


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

    @staticmethod
    def __format_by_level(fmt: str, level: int, /) -> str:
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
        """Format the specified record as text.

        The record's attribute dictionary is used as the operand to a string formatting
        operation which yields the returned string. Before formatting the dictionary, a
        couple of preparatory steps are carried out. The message attribute of the record
        is computed using LogRecord.getMessage(). If the formatting string uses the time
        (as determined by a call to usesTime(), formatTime() is called to format the
        event time. If there is exception information, it is formatted using
        formatException() and appended to the message.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: The formatted record as a string.
        """
        return self.__format_by_level(super().format(record), record.levelno)


def config_logging(
    logfile: str,
    *,
    console_logging: bool,
    colored_logs: bool,
    debug: bool,
    fmt: str = _DEFAULT_FMT,
    date_fmt: str = _DEFAULT_DATE_FMT,
) -> None:
    """Configure FizzBuzz's logging.

    Args:
        logfile (str): The file to log to.
        console_logging (bool): Whether to enable console logging.
        colored_logs (bool): Whether to color console logs.
        debug (bool): Whether to log debug messages.
        fmt (str, optional): The logging format to use. Defaults to _DEFAULT_FMT.
        date_fmt (str, optional): The logging date format to use.
            Defaults to _DEFAULT_DATE_FMT.
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
        f"FizzBuzz logging config: logfile={logfile}, debug={debug}, "
        f"no-console-logging={not console_logging}, colored-logs={colored_logs}"
    )


def cog_setup_log_msg(cog_name: str, bot: commands.Bot, /) -> str:
    """Create a log message for setting up a cog.

    Args:
        cog_name (str): The name of the cog being loaded.
        bot (commands.Bot): The bot being used by the cog.

    Returns:
        str: The log message.
    """
    if bot.user is None:
        logging.error("Unexpected logout")
        return f"Could not load {cog_name}"

    return (
        f"{cog_name} loaded | bot={bot.user} ({bot.user.id}) |"
        f"guilds={len(bot.guilds)} | commands={len(bot.commands)}"
    )


def log_app_command(interaction: discord.Interaction, /) -> None:
    """Log an app command interaction (debug only).

    Args:
        interaction (discord.Interaction): The interaction instance of the command.
    """
    cmd_name = (
        interaction.command.qualified_name if interaction.command else "unknown_command"
    )

    namespace = interaction.namespace
    params = " ".join(f"{k}={getattr(namespace, k)!r}" for k in vars(namespace))

    logging.debug("/%s %s invoked by %s", cmd_name, params, interaction.user)
