"""Help commands."""

import discord
from discord import app_commands
from discord.ext import commands

from ....util.pawprints import cog_setup_log_msg, log_app_command
from ...interaction import build_response_embed, report, safe_send
from ...ui.emoji import Status, Visual
from .help_registrator import (
    COMMAND_CATEGORIES,
    AppCommand,
    Category,
    HelpCarouselView,
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
        self.command_cache: list[AppCommand] | None = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(
        name="help", description="Get help regarding CatBot or a specific command"
    )
    @help_info("Help", examples=("/help",))
    async def help(
        self, interaction: discord.Interaction, command: str | None = None
    ) -> None:
        """Get help regarding CatBot or a command."""
        log_app_command(interaction)

        categories: dict[Category, list[AppCommand]] = {
            cat: [] for cat in COMMAND_CATEGORIES
        }

        # cache commands; they won't change after setup
        if not self.command_cache:
            self.command_cache = self.bot.tree.get_commands()

        for cmd in self.command_cache:
            info = get_help_info(cmd)
            if info is not None:
                categories[info.category].append(cmd)

        if not command:
            # add 1 to account for homepage
            embed, icon = build_help_homepage(len(COMMAND_CATEGORIES) + 1)
            view = HelpCarouselView(user=interaction.user, categories=categories)
            await view.send(interaction, embed=embed, files=[icon])
            return

        # else: command specified, find it
        command_object = None
        for command_list in categories.values():
            for cmd in command_list:
                if cmd.name == command:
                    command_object = cmd
                    break

        if command_object is None:
            await report(interaction, "That command does not exist!", Status.FAILURE)
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
