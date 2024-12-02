"""
moderation.py
Moderation tools for CatBot.
"""

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from ..confirm_button import ConfirmButton
from .command_logging import log_command

MAX_MESSAGE_DELETE_TIME = 604800
MAX_TIMEOUT_TIME = 86400
MESSAGE_WARNING_THRESHOLD = 5


class ManagementCog(commands.Cog, name="Management Commands"):
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

    @app_commands.command(name="echo", description="Echo a message.")
    @app_commands.describe(
        message="The message to echo.", channel="The channel to send the message."
    )
    async def echo(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: Optional[discord.TextChannel] = None,
    ) -> None:
        """
        Echo `message` to `channel`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param message: Message to echo
        :type message: str
        :param channel: Channel to echo the message to;
        sends to the current channel if None, defaults to None
        :type channel: discord.TextChannel | None, optional
        """

        logging.info(
            "/echo message=%s channel=%s invoked by %s",
            message,
            channel,
            interaction.user,
        )
        await log_command(
            "echo", interaction.user, self.bot, message=message, channel=channel
        )

        if channel is None:
            channel = interaction.channel  # type: ignore

        try:
            await channel.send(message)  # type: ignore
            await interaction.response.send_message("Echoed message.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to send messages in this channel.",
                ephemeral=True,
            )
            logging.warning(
                "Failed to echo message due to lack of permissions in channel %s",
                channel,
            )

    @app_commands.command(name="dm", description="Send a DM to a user.")
    @app_commands.describe(
        user="User to send the DM to.",
        message="The message to send.",
    )
    async def dm(
        self, interaction: discord.Interaction, user: discord.User, message: str
    ) -> None:
        """
        DM `user` with `message`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to DM
        :type user: discord.User
        :param message: Message to send to `user`
        :type message: str
        """

        logging.info(
            "/dm user=%s message=%s invoked by %s",
            user,
            message,
            interaction.user,
        )
        await log_command("dm", interaction.user, self.bot, user=user, message=message)

        try:
            await user.send(message)  # type: ignore
            await interaction.response.send_message("DM sent.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to send DMs to this user.", ephemeral=True
            )
            logging.info(
                "Failed to send DM to user %s; they likely have DMs disabled", user
            )

    @app_commands.command(name="announce", description="Announce a message.")
    @app_commands.describe(
        message="The message to announce.",
        channel="The channel to send the message.",
        ping="The role to ping.",
    )
    async def announce(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: Optional[discord.TextChannel] = None,
        ping: Optional[discord.Role] = None,
    ) -> None:
        """
        Create an announcement in `channel` with `message` and optionally ping `ping`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param message: Announcement message
        :type message: str
        :param channel: Channel to announce in;
        sends in current channel if None, defaults to None
        :type channel: Optional[discord.TextChannel], optional
        :param ping: Role to ping if not None, defaults to None
        :type ping: Optional[discord.Role], optional
        """

        logging.info(
            "/announce message=%s channel=%s ping=%s invoked by %s",
            message,
            channel,
            ping,
            interaction.user,
        )
        await log_command(
            "announce",
            interaction.user,
            self.bot,
            message=message,
            channel=channel,
            ping=ping,
        )

        if channel is None:
            channel = interaction.channel  # type: ignore

        # @everyone role has same ID as guild ID
        ping_is_at_everyone = ping == interaction.guild.get_role(  # type: ignore
            interaction.guild_id  # type: ignore
        )
        if ping is not None:
            if ping_is_at_everyone:
                message = f"{message}\n-# {ping}"
            else:
                message = f"{message}\n-# {ping.mention}"

        async def attempt_send() -> None:
            try:
                await channel.send(message)  # type: ignore
            except discord.Forbidden:
                await interaction.response.send_message(
                    "I don't have permission to send messages in this channel.",
                    ephemeral=True,
                )
                logging.warning(
                    "Failed to send announcement due to lack of permissions in channel %s",
                    channel,
                )

        if ping_is_at_everyone:  # type: ignore
            view = ConfirmButton(
                interaction, "Announcement sent.", "Announcement cancelled."
            )
            view.on_confirmation(attempt_send)

            await interaction.response.send_message(
                "Are you sure you want to ping everyone with this announcement?",
                view=view,
                ephemeral=True,
            )
        else:
            await attempt_send()
            await interaction.response.send_message(
                "Announcement sent.", ephemeral=True
            )


async def setup(bot: commands.Bot):
    """
    Set up the ManagementCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(ManagementCog(bot))