"""
moderation.py
Moderation tools for CatBot.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands

from ..bot_init import MODERATOR_ROLES, TIME_MULTIPLICATION_TABLE
from ..confirm_button import ConfirmButton
from ..internal_utils import wrap_reason
from .command_logging import log_command

MAX_MESSAGE_DELETE_TIME = 604800
MAX_TIMEOUT_TIME = 86400
MESSAGE_WARNING_THRESHOLD = 5


# IMPORTANT:
# We DO NOT use interaction.response.send_response()
# for successful completion of any moderation commands
# that require button verification here.
# This is because ConfirmButton already sends a response
# on confirmation or denial of admin commands.
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

    timeout_group = app_commands.Group(
        name="timeout", description="Tools for timing out users"
    )

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.describe(
        user="User to ban",
        delete_message_time="How much of the user's message history to delete",
        time_unit="Unit of time",
        reason="Ban reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def ban(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        user: discord.User,
        delete_message_time: int = 0,
        time_unit: Literal["seconds", "minutes", "hours", "days"] = "seconds",
        reason: Optional[str] = None,
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
        :type reason: str | None, optional
        """

        logging.info(
            "/ban user=%s delete_message_time=%s time_unit=%s reason=%s invoked by %s",
            user,
            delete_message_time,
            time_unit,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "ban",
            interaction.user,
            self.bot,
            user=user,
            delete_message_time=delete_message_time,
            time_unit=time_unit,
            reason=repr(reason),
        )

        delete_message_time = max(delete_message_time, 0)
        if reason is None:
            reason = "No reason provided."

        async def attempt_ban() -> None:
            try:

                await interaction.guild.ban(  # type: ignore
                    user,
                    reason=wrap_reason(reason, interaction.user),
                    delete_message_seconds=min(
                        MAX_MESSAGE_DELETE_TIME,
                        delete_message_time * TIME_MULTIPLICATION_TABLE[time_unit],
                    ),
                )
                logging.info("Successfully banned %s", user)

                try:
                    await user.send(
                        f"You have been banned from **{interaction.guild.name}**."  # type: ignore
                        + f"\nReason: {reason}"
                    )
                    logging.info("%s messaged successfully", user)
                except discord.Forbidden:
                    logging.info("Could not DM %s; they may have DMs disabled", user)

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

    @app_commands.command(name="unban", description="Unban a user from")
    @app_commands.describe(
        user_id="ID of the user to unban",
        reason="Unban reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: Optional[str] = None,
    ):
        """
        Unban `user` from the guild with optional ability to provide a reason.

        :param interaction: The interaction instance.
        :type interaction: discord.Interaction
        :param user_id: ID of user to unban
        :type user_id: str
        :param reason: Reason for the unban, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/unban user_id=%s reason=%s invoked by user %s",
            user_id,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "unban", interaction.user, self.bot, user_id=user_id, reason=repr(reason)
        )

        try:
            int_user_id = int(user_id)
        except TypeError:
            await interaction.response.send_message(
                "Invalid user ID entered.", ephemeral=True
            )
            return

        if reason is None:
            reason = "No reason provided."

        user = await interaction.client.fetch_user(int_user_id)  # type: ignore

        async def attempt_unban():
            try:
                await interaction.guild.unban(user, reason=wrap_reason(reason, interaction.user))  # type: ignore
                logging.info("%s was successfully unbanned", user)

                try:
                    await user.send(
                        "You have been unbanned from"
                        + f" **{interaction.guild.name}.**"  # type: ignore
                        + "\nReason: {reason}"
                    )
                    logging.info("Messaged %s successfully", user)

                except AttributeError:
                    await interaction.response.send_message(
                        "User does not exist.", ephemeral=True
                    )
                    logging.info("User %s does not exist", user)
                    return

                except discord.Forbidden:
                    logging.info("Could not DM %s; they may have DMs disabled", user)

            except discord.Forbidden:
                await interaction.response.send_message(
                    "I do not have permissions to ban this member.", ephemeral=True
                )
                logging.warning("Failed to ban member due to lack of permissions")
            except discord.NotFound:
                await interaction.response.send_message(
                    f"User {user} was not found.", ephemeral=True
                )
                logging.info("%s was not found", user)

        view = ConfirmButton(
            interaction, f"{user} was unbanned successfully.", "Cancelled unban."
        )
        view.on_confirmation(attempt_unban)
        await interaction.response.send_message(
            f"Are you sure you want to unban {user}?", view=view, ephemeral=True
        )

    @timeout_group.command(name="add", description="Add time to a user's timeout")
    @app_commands.describe(
        user="User to add timeout time to",
        time="Timeout duration",
        time_unit="Unit of time",
        reason="Timeout reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def timeout_add(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        time: int,
        time_unit: Literal["seconds", "minutes", "hours", "days"] = "seconds",
        reason: Optional[str] = None,
    ) -> None:
        """
        Add `time` `unit` to `user`'s timeout duration.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to add timeout to
        :type user: discord.Member
        :param time: Timeout duration
        :type time: int
        :param time_unit: Unit of time, defaults to "seconds"
        :type time_unit: Literal["seconds", "minutes", "hours", "days"], optional
        :param reason: Timeout reason, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/timeout add user=%s time=%s time_unit=%s reason=%s invoked by %s",
            user,
            time,
            time_unit,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "timeout add",
            interaction.user,
            self.bot,
            user=user,
            time=time,
            time_unit=time_unit,
            reason=repr(reason),
        )

        time = max(time, 0)
        reason = "No reason provided." if reason is None else reason

        max_timeout_date = datetime.now(timezone.utc) + timedelta(
            seconds=MAX_TIMEOUT_TIME
        )

        if user.timed_out_until is not None:
            timed_out_until = user.timed_out_until + timedelta(
                seconds=time * TIME_MULTIPLICATION_TABLE[time_unit]
            )
        else:
            timed_out_until = datetime.now(timezone.utc) + timedelta(
                seconds=time * TIME_MULTIPLICATION_TABLE[time_unit]
            )

        if timed_out_until > max_timeout_date:
            timed_out_until = max_timeout_date
            time_maxed = True
        else:
            time_maxed = False

        try:
            await user.timeout(timed_out_until, reason=reason)
            if time_maxed:
                await interaction.response.send_message(
                    f"{user}'s timeout set to 1 day (maximum timeout duration).",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"{user}'s timeout extended by {time} {time_unit}.",
                    ephemeral=True,
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permissions to timeout this user.", ephemeral=True
            )
            logging.warning("Failed to add timeout to user due to lack of permissions")
        except discord.NotFound:
            await interaction.response.send_message(
                f"User {user} was not found.", ephemeral=True
            )
            logging.info("User %s was not found", user)

    @timeout_group.command(
        name="reduce", description="Reduce a user's timeout duration"
    )
    @app_commands.describe(
        user="User to reduce the timeout of",
        time="Time reduction amount",
        time_unit="Unit of time",
        reason="Timeout reduction reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def timeout_reduce(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        time: int,
        time_unit: Literal["seconds", "minutes", "hours", "days"] = "seconds",
        reason: Optional[str] = None,
    ) -> None:
        """
        Subtract `time` `unit` from `user`'s timeout duration.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to reduce the timeout of
        :type user: discord.Member
        :param time: Timeout duration
        :type time: int
        :param time_unit: Unit of time, defaults to "seconds"
        :type time_unit: Literal["seconds", "minutes", "hours", "days"], optional
        :param reason: Timeout reason, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/timeout reduce user=%s time=%s time_unit=%s reason=%s invoked by %s",
            user,
            time,
            time_unit,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "timeout reduce",
            interaction.user,
            self.bot,
            user=user,
            time=time,
            time_unit=time_unit,
            reason=repr(reason),
        )

        if reason is None:
            reason = "No reason provided."

        if user.timed_out_until is None:
            await interaction.response.send_message(
                "User is not timed out.", ephemeral=True
            )
            return

        timed_out_until = user.timed_out_until - timedelta(
            seconds=time * TIME_MULTIPLICATION_TABLE[time_unit]
        )

        try:
            await user.timeout(
                timed_out_until, reason=wrap_reason(reason, interaction.user)
            )
            await interaction.response.send_message(
                f"{user}'s timeout reduced by {time} {time_unit}.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permissions to timeout this user.", ephemeral=True
            )
            logging.warning(
                "Failed to reduce user's timeout due to lack of permissions"
            )
        except discord.NotFound:
            await interaction.response.send_message(
                f"User {user} was not found.", ephemeral=True
            )
            logging.info("User %s was not found", user)

    @timeout_group.command(name="remove", description="Remove a user's timeout")
    @app_commands.describe(
        user="User to remove the timeout from",
        reason="Timeout removal reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def timeout_remove(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = None,
    ) -> None:
        """
        Remove `user`'s timeout.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to remove timeout from
        :type user: discord.Member
        :param reason: Timeout removal reason, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/timeout remove user=%s reason=%s invoked by %s",
            user,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "timeout remove",
            interaction.user,
            self.bot,
            user=user,
            reason=repr(reason),
        )

        if reason is None:
            reason = "No reason provided."

        if not user.is_timed_out():
            await interaction.response.send_message(
                "User is not timed out.", ephemeral=True
            )
            return

        try:
            await user.timeout(None, reason=wrap_reason(reason, interaction.user))
            await interaction.response.send_message(
                f"{user}'s timeout was removed.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permissions to timeout this user.", ephemeral=True
            )
            logging.warning(
                "Failed to reduce user's timeout due to lack of permissions"
            )
        except discord.NotFound:
            await interaction.response.send_message(
                f"User {user} was not found.", ephemeral=True
            )
            logging.info("User %s was not found", user)

    @app_commands.command(
        name="clear", description="Delete a number of messages from a channel"
    )
    @app_commands.describe(
        amount="Number of messages to delete",
        channel="Channel to delete messages from",
        reason="Deletion reason",
    )
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: int,
        channel: Optional[discord.TextChannel] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Delete `amount` messages from `channel`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param amount: Number of messages to delete
        :type amount: int
        :param channel: Channel to delete messages from
        (None means current channel), defaults to None
        :type channel: Optional[discord.TextChannel], optional
        :param reason: Reason for message deletion, defaults to None
        :type reason: str | None, optional
        """

        if channel is None:
            channel = interaction.channel  # type: ignore

        logging.info(
            "/clear amount=%s channel=%s reason=%s invoked by %s",
            amount,
            channel,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "clear",
            interaction.user,
            self.bot,
            amount=amount,
            channel=channel,
            reason=repr(reason),
        )

        if reason is None:
            reason = "No reason provided."

        async def attempt_purge(channel: discord.TextChannel) -> None:
            try:
                await channel.purge(
                    limit=amount, reason=wrap_reason(reason, interaction.user)
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    f"I do not have permissions to delete messages in {channel}.",
                    ephemeral=True,
                )
                logging.warning("Failed to delete messages due to lack of permissions")

        if amount <= MESSAGE_WARNING_THRESHOLD:
            await interaction.response.defer(ephemeral=True)

            try:
                await channel.purge(limit=amount)  # type: ignore
                await interaction.followup.send(
                    f"Successfully cleared {amount} messages from {channel}.",
                    ephemeral=True,
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    f"I do not have permissions to delete messages in {channel}.",
                    ephemeral=True,
                )
                logging.warning("Failed to delete message due to lack of permissions")

            return

        view = ConfirmButton(
            interaction,
            f"Successfully cleared {amount} messages from {channel}.",
            "Cancelled message clearing.",
        )
        view.on_confirmation(attempt_purge, channel)
        await interaction.response.send_message(
            f"Are you sure you want to clear {amount} messages from {channel}?",
            view=view,
            ephemeral=True,
        )

    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(
        user="User to warn",
        reason="Warning reason",
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        channel: Optional[discord.TextChannel] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Warn `user` with `reason`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to warn
        :type user: discord.Member
        :param channel: Channel to send warning message to;
        sends the message to the current channel if None, defaults to None
        :type channel: discord.TextChannel | None, optional
        :param reason: Warning reason, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/warn user=%s channel=%s reason=%s invoked by %s",
            user,
            channel,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "warn",
            interaction.user,
            self.bot,
            user=user,
            channel=channel,
            reason=repr(reason),
        )

        if channel is None:
            channel = interaction.channel  # type: ignore

        if reason is None:
            reason = "No reason provided."

        await channel.send(  # type: ignore
            f"{user.mention}, you have been warned.\nReason: {reason}"
        )
        await interaction.response.send_message(
            f"{user} has been warned.", ephemeral=True
        )

    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.describe(
        user="User to kick",
        reason="Kick reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def kick(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = None,
    ) -> None:
        """
        Kick `user` with `reason`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to kick
        :type user: discord.Member
        :param reason: Kick reason, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/kick user=%s reason=%s invoked by %s",
            user,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "kick", interaction.user, self.bot, user=user, reason=repr(reason)
        )

        if reason is None:
            reason = "No reason provided."

        async def attempt_kick():
            try:
                await user.kick(reason=wrap_reason(reason, interaction.user))
            except discord.Forbidden:
                await interaction.response.send_message(
                    "I do not have permissions to kick this user.", ephemeral=True
                )
                logging.warning("Failed to kick user due to lack of permissions")

        view = ConfirmButton(
            interaction, f"{user} kicked successfully.", "Cancelled kick."
        )
        view.on_confirmation(attempt_kick)
        await interaction.response.send_message(
            f"Are you sure you want to kick {user}?", view=view, ephemeral=True
        )

    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.describe(
        user="User to mute",
        reason="Mute reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def mute(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = None,
    ) -> None:
        """
        Mute `user` with `reason`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to mute
        :type user: discord.Member
        :param reason: Mute reason, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/mute user=%s reason=%s invoked by %s",
            user,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "mute", interaction.user, self.bot, user=user, reason=repr(reason)
        )

        if reason is None:
            reason = "No reason provided."

        try:
            await user.edit(mute=True, reason=wrap_reason(reason, interaction.user))
            await interaction.response.send_message(
                f"{user} has been muted.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permissions to mute this user.", ephemeral=True
            )
            logging.warning("Failed to mute user due to lack of permissions")
        except discord.HTTPException:
            await interaction.response.send_message(
                "An error occurred while attempting to mute the user. "
                + "This is likely because they are not in a voice channel. "
                + "If this isn't the case, please report this to @zentiph!",
                ephemeral=True,
            )

    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.describe(
        user="User to unmute",
        reason="Unmute reason",
    )
    @app_commands.checks.has_any_role(*MODERATOR_ROLES)
    async def unmute(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = None,
    ) -> None:
        """
        Unmute `user` with `reason`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param user: User to unmute
        :type user: discord.Member
        :param reason: Unmute reason, defaults to None
        :type reason: str | None, optional
        """

        logging.info(
            "/unmute user=%s reason=%s invoked by %s",
            user,
            repr(reason),
            interaction.user,
        )
        await log_command(
            "unmute", interaction.user, self.bot, user=user, reason=repr(reason)
        )

        if reason is None:
            reason = "No reason provided."

        try:
            await user.edit(mute=False, reason=wrap_reason(reason, interaction.user))
            await interaction.response.send_message(
                f"{user} has been unmuted.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permissions to unmute this user.", ephemeral=True
            )
            logging.warning("Failed to unmute user due to lack of permissions")
        except discord.HTTPException:
            await interaction.response.send_message(
                "An error occurred while attempting to unmute the user. "
                + "This is likely because they are not in a voice channel. "
                + "If this isn't the case, please report this to @zentiph!",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    """
    Set up the ModerationCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(ModerationCog(bot))
