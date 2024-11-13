"""
moderation.py
Moderation tools for CatBot.
"""

from datetime import datetime, timedelta, timezone
from enum import StrEnum
import logging
from typing import Any, Literal, Union

import discord
from discord import app_commands
from discord.ext import commands

from ..internal import LOGGING_CHANNEL, TIME_MULTIPLICATION_TABLE
from ..confirm_button import ConfirmButton


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


# IMPORTANT:
# We DO NOT use interaction.response.send_response()
# for successful completion of moderation commands here.
# This is because ConfirmButton already sends a response
# on confirmation or denial of admin commands, so this
# is unnecessary.
class ModerationCog(commands.Cog, name="Moderation Commands"):
    """
    Cog containing moderation commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Run when the cog is ready to be used.
        """

        logging.info("ModerationCog loaded")

    async def log_command(
        self,
        cmd_name: str,
        caller: Union[discord.User, discord.Member],
        /,
        **cmd_args: Any,
    ) -> None:
        """
        Log a command's usage.

        :param cmd_name: Name of the command
        :type cmd_name: str
        :param caller: User who called the command
        :type caller: discord.User | discord.Member
        :param cmd_args: Arguments given to the command
        :type cmd_args: Any
        """

        def generate_log_message(cmd_name, caller, **cmd_args):
            msg = (
                "```ansi\n"
                + AnsiFormats.gray
                + f"[{datetime.now()}]\n"
                + AnsiFormats.bold_yellow
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

        channel = self.bot.get_channel(LOGGING_CHANNEL)
        if isinstance(channel, discord.TextChannel):
            await channel.send(generate_log_message(cmd_name, caller, **cmd_args))

        elif channel is None or isinstance(channel, discord.abc.PrivateChannel):
            logging.error("Could not find logging channel")
        else:
            logging.error("Cannot log to %s; it is not a TextChannel", channel.name)

    timeout_group = app_commands.Group(
        name="timeout", description="Tools for timing out users"
    )

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.describe(
        user="User to ban",
        delete_message_time="How much of the user's message history to delete",
        time_unit="Unit of time",
        reason="Ban reason",
        ghost="Don't notify the user",
    )
    @app_commands.checks.has_any_role("Owner", "Management", "Mod")
    async def ban(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        user: discord.User,
        delete_message_time: int = 0,
        time_unit: Literal["seconds", "minutes", "hours", "days"] = "seconds",
        reason: Union[str, None] = None,
        ghost: bool = False,
    ) -> None:
        """
        Ban `user` from the guild.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to ban
        :type user: discord.User
        :param delete_message_time: The amount of `user`'s message history to delete, defaults to 0
        :type delete_message_time: int, optional
        :param time_unit: Unit of time, defaults to "seconds"
        :type time_unit: Literal["seconds", "minutes", "hours", "days"], optional
        :param reason: Reason for the ban, defaults to None
        :type reason: Union[str, None], optional
        :param ghost: Whether to NOT notify the user, defaults to False
        :type ghost: bool, optional
        """

        logging.info(
            "/ban user=%s delete_message_time=%s time_unit=%s reason=%s ghost=%s invoked by %s",
            user,
            delete_message_time,
            time_unit,
            reason,
            ghost,
            interaction.user,
        )
        await self.log_command(
            "ban",
            interaction.user,
            user=user,
            delete_message_time=delete_message_time,
            time_unit=time_unit,
            reason=reason,
            ghost=ghost,
        )

        delete_message_time = max(delete_message_time, 0)
        if reason is None:
            reason = "No reason provided."

        async def attempt_ban():
            if not ghost:
                try:
                    await user.send(
                        f"You have been banned from **{interaction.guild.name}** "
                        + f"by **{interaction.user}**.\nReason: {reason}"
                    )
                    logging.info("%s messaged successfully", user)
                except discord.Forbidden:
                    logging.info("Could not DM %s; they may have DMs disabled", user)

            try:

                await interaction.guild.ban(
                    user,
                    reason=reason,
                    delete_message_seconds=min(
                        604800,  # Max message delete time
                        delete_message_time * TIME_MULTIPLICATION_TABLE[time_unit],
                    ),
                )
                logging.info("Successfully banned %s", user)
            except discord.Forbidden:
                await interaction.response.send_message(
                    "I do not have permission to ban this member.", ephemeral=True
                )
                logging.warning("Failed to ban member due to inadequate permissions")
            except discord.NotFound:
                await interaction.response.send_message(
                    f"User **{user}** was not found.", ephemeral=True
                )
                logging.info("%s was not found", user)

        view = ConfirmButton(
            interaction, f"{user} banned successfully.", f"Cancelled banning {user}."
        )
        view.on_confirmation(attempt_ban)

        await interaction.response.send_message(
            f"Are you sure you want to ban {user}?", view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    """
    Set up the ModerationCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(ModerationCog(bot))
