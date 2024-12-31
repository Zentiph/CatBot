"""
help.py
Help cog for CatBot.
"""

import logging
from typing import Union, Tuple

import discord
from discord import app_commands
from discord.ext import commands

from .. import emojis
from ..internal_utils import (
    DEFAULT_EMBED_COLOR,
    generate_authored_embed_with_icon,
)
from .commands import (
    COLOR,
    DATETIME,
    FUN,
    HELP,
    MANAGEMENT,
    MATH,
    MODERATION,
    RANDOM,
    PRIVATE_COMMAND_MAP,
    PUBLIC_COMMAND_MAP,
    ClassifiedHelpCategory,
    HelpCategory,
)
from .representations import generate_field_description, generate_field_title

CATEGORY_MAP = {
    "color": COLOR,
    "date-time": DATETIME,
    "fun": FUN,
    "help": HELP,
    "math": MATH,
    "random": RANDOM,
    "management": MANAGEMENT,
    "moderation": MODERATION,
}


def generate_help_embed(
    category: Union[HelpCategory, ClassifiedHelpCategory]
) -> Tuple[discord.Embed, discord.File]:
    """
    Generate a help embed with the given category.

    :param category: Help category
    :type category: HelpCategory | ClassifiedHelpCategory
    :return: Tuple containing the embed and icon file
    :rtype: Tuple[discord.Embed, discord.File]
    """

    embed, icon = generate_authored_embed_with_icon(
        embed_title=f"{emojis.QUESTION_MARK} {category.title()} Commands Help Page",
        embed_description=f"Here's a list of {category} commands and how to use them.",
    )

    for command in CATEGORY_MAP[category]:
        embed.add_field(
            name=generate_field_title(command),
            value=generate_field_description(command),
            inline=False,
        )

    return embed, icon


class HelpCog(commands.Cog, name="Help Commands"):
    """
    Cog containing help commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("HelpCog loaded")

    help_group = app_commands.Group(
        name="help", description="Get help for using the bot"
    )

    @help_group.command(
        name="category", description="List all the commands in a category"
    )
    @app_commands.describe(category="Category of commands to get help for")
    async def help_category(
        self,
        interaction: discord.Interaction,
        category: HelpCategory,
    ) -> None:
        """
        Get help for `category`.
        """

        logging.info(
            "/help category category=%s invoked by %s", category, interaction.user
        )

        embed, icon = generate_help_embed(category)
        await interaction.response.send_message(embed=embed, file=icon)

    @help_group.command(
        name="command", description="Get help regarding a specific command"
    )
    @app_commands.describe(cmd="Command to get help for")
    async def help_command(self, interaction: discord.Interaction, cmd: str) -> None:
        """
        Get help for `cmd`.
        """

        logging.info("/help command cmd=%s invoked by %s", repr(cmd), interaction.user)

        command = PUBLIC_COMMAND_MAP.get(cmd, None)
        if command is None:
            await interaction.response.send_message(
                f"{emojis.X} I do not have a command called **{cmd}**.", ephemeral=True
            )
            return

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.QUESTION_MARK} {cmd} Help Page",
            embed_description=f"Here's how to use **{cmd}**.",
            embed_color=DEFAULT_EMBED_COLOR,
        )

        embed.add_field(
            name=generate_field_title(command),
            value=generate_field_description(command),
        )

        await interaction.response.send_message(embed=embed, file=icon)


class ClassifiedHelpCog(commands.Cog, name="Moderation Help Commands"):
    """
    Cog containing moderator-only help commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("ClassifiedHelpCog loaded")

    help_group = app_commands.Group(
        name="mod-help", description="Get help for using the bot's moderation commands"
    )

    @help_group.command(
        name="category", description="List all the commands in a category"
    )
    @app_commands.describe(category="Category of commands to get help for")
    async def help_category(
        self,
        interaction: discord.Interaction,
        category: ClassifiedHelpCategory,
    ) -> None:
        """
        Get help for `category`.
        """

        logging.info(
            "/help-mod category category=%s invoked by %s", category, interaction.user
        )

        embed, icon = generate_help_embed(category)
        await interaction.response.send_message(embed=embed, file=icon)

    @help_group.command(
        name="command", description="Get help regarding a specific command"
    )
    @app_commands.describe(cmd="Command to get help for")
    async def help_command(self, interaction: discord.Interaction, cmd: str) -> None:
        """
        Get help for `cmd`.
        """

        logging.info(
            "/help-mod command cmd=%s invoked by %s", repr(cmd), interaction.user
        )

        command = PRIVATE_COMMAND_MAP.get(cmd, None)
        if command is None:
            await interaction.response.send_message(
                f"{emojis.X} I do not have a private command called **{cmd}**.",
                ephemeral=True,
            )
            return

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.QUESTION_MARK} {cmd} Help Page",
            embed_description=f"Here's how to use **{cmd}**.",
            embed_color=DEFAULT_EMBED_COLOR,
        )

        embed.add_field(
            name=generate_field_title(command),
            value=generate_field_description(command),
        )

        await interaction.response.send_message(embed=embed, file=icon)


async def setup(bot: commands.Bot):
    """
    Set up the HelpCog and ClassifiedHelpCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(HelpCog(bot))
    await bot.add_cog(ClassifiedHelpCog(bot))
