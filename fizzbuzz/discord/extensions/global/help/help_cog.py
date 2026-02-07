"""Help commands."""

import discord
from discord import app_commands
from discord.ext import commands

from .....util.log_handler import cog_setup_log_msg, log_app_command
from ....interaction import build_response_embed, report, safe_send
from ....ui.emoji import Status, Visual
from .help_registrator import (
    AppCommand,
    build_command_info_str,
    build_help_homepage,
    get_help_info,
    help_info,
)

__author__ = "Gavin Borne"
__license__ = "MIT"


class HelpCog(commands.Cog, name="Help Commands"):
    """Cog containing help commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create the HelpCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot
        self.command_cache: dict[str, AppCommand] = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(
        name="help", description="Get help regarding FizzBuzz or a specific command"
    )
    @app_commands.describe(command="The command to get help for")
    @help_info(
        "Help",
        "Get help regarding FizzBuzz in general, or a specific command.",
        examples=("/help", "/help command:color"),
    )
    async def help(
        self, interaction: discord.Interaction, command: str | None = None
    ) -> None:
        """Get help regarding FizzBuzz or a command."""
        log_app_command(interaction)

        # cache commands; they won't change after setup
        if not self.command_cache:
            for cmd in self.bot.tree.get_commands():
                info = get_help_info(cmd)
                if info is not None:
                    self.command_cache[cmd.name] = cmd

        if not command:
            embed, icon = build_help_homepage()
            await safe_send(interaction, embed=embed, files=[icon])
            return

        # else: command specified, find it
        command_object = self.command_cache.get(command)
        if command_object is None:
            await report(
                interaction,
                f"The command '{command}' does not exist, "
                "or does not yet have dedicated help info.",
                Status.FAILURE,
            )
            return

        help_info = get_help_info(command_object)
        # shouldn't be None here, but checking for type-checkers.
        if help_info is None:
            await report(
                interaction,
                "There is no help information for this command.",
                Status.FAILURE,
            )
            return

        embed, icon = build_response_embed(
            title=f"{Visual.QUESTION_MARK} /{command} Help",
            description=build_command_info_str(command_object, help_info),
        )
        await safe_send(interaction, embed=embed, file=icon)


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(HelpCog(bot))
