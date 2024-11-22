"""
command_logging.py
Code for logging commands.
"""

import logging
from datetime import datetime
from enum import StrEnum
from typing import Any, Union

import discord

from ..bot_init import LOGGING_CHANNEL


# pylint: disable=invalid-name
class AnsiFormats(StrEnum):
    """
    ANSI formats for logging commands.
    """

    reset = "\u001b[0m"
    gray = "\u001b[0;30m"
    bold_gray = "\u001b[1;30m"
    underlined_gray = "\u001b[4;30m"
    red = "\u001b[0;31m"
    bold_red = "\u001b[1;31m"
    underlined_red = "\u001b[4;31m"
    green = "\u001b[0;32m"
    bold_green = "\u001b[1;32m"
    underlined_green = "\u001b[4;32m"
    yellow = "\u001b[0;33m"
    bold_yellow = "\u001b[1;33m"
    underlined_yellow = "\u001b[4;33m"
    blue = "\u001b[0;34m"
    bold_blue = "\u001b[1;34m"
    underlined_blue = "\u001b[4;34m"
    pink = "\u001b[0;35m"
    bold_pink = "\u001b[1;35m"
    underlined_pink = "\u001b[4;35m"
    cyan = "\u001b[0;36m"
    bold_cyan = "\u001b[1;36m"
    underlined_cyan = "\u001b[4;36m"
    white = "\u001b[0;37m"
    bold_white = "\u001b[1;37m"
    underlined_white = "\u001b[4;37m"


async def log_command(
    cmd_name: str,
    caller: Union[discord.User, discord.Member],
    bot: discord.ext.commands.Bot,
    /,
    **cmd_args: Any,
) -> None:
    """
    Log a command's usage.

    :param cmd_name: Name of the command
    :type cmd_name: str
    :param caller: User who called the command
    :type caller: discord.User | discord.Member
    :param bot: Bot to use for logging
    :type bot: discord.ext.commands.Bot
    :param cmd_args: Arguments given to the command
    :type cmd_args: Any
    """

    def generate_log_message(cmd_name, caller, **cmd_args):
        msg = (
            "```ansi\n"
            + AnsiFormats.gray
            + f"[{datetime.now()}]\n"
            + AnsiFormats.yellow
            + f"/{cmd_name}"
        )
        for name, value in cmd_args.items():
            msg += (
                " "
                + AnsiFormats.pink
                + name
                + AnsiFormats.reset
                + "="
                + AnsiFormats.white
                + str(value)
            )
        msg += (
            AnsiFormats.reset
            + "\ncalled by "
            + AnsiFormats.cyan
            + caller.name
            + "\n```"
        )
        return msg

    channel = bot.get_channel(LOGGING_CHANNEL)
    if isinstance(channel, discord.TextChannel):
        await channel.send(generate_log_message(cmd_name, caller, **cmd_args))

    elif channel is None or isinstance(channel, discord.abc.PrivateChannel):
        logging.error("Could not find logging channel")
    else:
        logging.error("Cannot log to %s; it is not a TextChannel", channel.name)
