"""
help.py
Help cog for CatBot.
"""

import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from .internal import DEFAULT_EMBED_COLOR
from .commands import ALL, COLOR_ROLES, COLOR_TOOLS, COMMAND_MAP
from .representations import (
    generate_field_description,
    generate_field_title,
)

HelpCategory = Literal["color roles", "color tools"]


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

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param category: Category to get help for
        :type category: HelpCategory
        """

        logging.info(
            "/help category category=%s invoked by %s", category, interaction.user
        )

        match category:
            case "color roles":
                embed = discord.Embed(
                    title="Color Roles Commands Help Page",
                    description="Here's a list of color roles commands and how to use them.",
                    color=DEFAULT_EMBED_COLOR,
                )
                for command in COLOR_ROLES:
                    embed.add_field(
                        name=generate_field_title(command),
                        value=generate_field_description(command),
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed)

            case "color tools":
                embed = discord.Embed(
                    title="Color Tools Commands Help Page",
                    description="Here's a list of color tools commands and how to use them.",
                    color=DEFAULT_EMBED_COLOR,
                )
                for command in COLOR_TOOLS:
                    embed.add_field(
                        name=generate_field_title(command),
                        value=generate_field_description(command),
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed)

            case _:
                await interaction.response.send_message(
                    "You have entered an incorrect category.", ephemeral=True
                )
                # This shouldn't be possible
                logging.warning(
                    "/help category category=%s was not stopped by Discord type-checking",
                    category,
                )

    @help_group.command(
        name="command", description="Get help regarding a specific command."
    )
    @app_commands.describe(cmd="Command to get help for")
    async def help_command(self, interaction: discord.Interaction, cmd: str) -> None:
        """
        Get help for `cmd`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param cmd: Command to get help for
        :type cmd: str
        """

        logging.info("/help command cmd=%s", cmd)

        if cmd not in (command.name for command in ALL) and cmd not in (
            f"{command.group} {command.name}" for command in ALL
        ):
            await interaction.response.send_message(
                f"I do not have a command called '{cmd}'!", ephemeral=True
            )
            return

        command = COMMAND_MAP[cmd]
        embed = discord.Embed(
            title=f"{cmd} Help Page",
            description=f"Here's how to use {cmd}.",
            color=DEFAULT_EMBED_COLOR,
        )
        embed.add_field(
            name=generate_field_title(command),
            value=generate_field_description(command),
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Set up the HelpCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(HelpCog(bot))
