"""
experimental.py
Experimental cog for CatBot.
To be used when testing or developing new features or ideas.
Should NOT be loaded unless in testing mode.
"""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from ..internal_utils import (
    DEFAULT_EMBED_COLOR,
    generate_authored_embed,
    generate_image_file,
)


class ExperimentalCog(commands.Cog, name="Help Commands"):
    """
    Cog containing experimental commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("ExperimentalCog loaded")

    # @app_commands.command(name="star-args-experiment")
    # async def
