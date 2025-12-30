"""Class declaration for CatBot, a subclass of discord.py's Bot class."""

import discord
from discord.ext import commands

__author__ = "Gavin Borne"
__license__ = "MIT"


class CatBot(commands.Bot):
    """A Bot with preset intents."""

    def __init__(self) -> None:
        """A Bot with preset intents.

        Args:
            store (YearlyMetricStore): Where to store metrics information.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)
