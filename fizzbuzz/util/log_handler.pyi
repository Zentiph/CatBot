# pylint:disable=all
from enum import StrEnum
import logging
from typing import Final

import discord
from discord.ext import commands

__author__: Final[str]
__license__: Final[str]

LOG_FILE: Final[str]

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
    fmt: str = ...,
    date_fmt: str = ...,
) -> None: ...
def cog_setup_log_msg(cog_name: str, bot: commands.Bot, /) -> str: ...
def log_app_command(interaction: discord.Interaction, /) -> None: ...
