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


class ExperimentalCog(commands.Cog, name="Experimental Stuff"):
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


async def setup(bot: commands.Bot):
    """
    Set up the ExperimentalCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(ExperimentalCog(bot))
