"""
help.py
Help cog for CatBot.
"""

import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands


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
        category: Literal["user-assigned roles", "colors", "fun", "moderation"],
    ) -> None:
        """
        Get help for `category`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param category: Category to get help for
        :type category: Literal["user-assigned roles", "colors", "fun", "moderation"]
        """

        match category:
            case "colors":
                ...
            case "fun":
                ...
            case "moderation":
                ...
            case "user-assigned roles":
                ...
