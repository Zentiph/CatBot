"""Class declaration for CatBot, a subclass of discord.py's Bot class."""

import discord
from discord.ext import commands

from ..db.cat_scan import YearlyMetricStore

__author__ = "Gavin Borne"
__license__ = "MIT"


class CatBot(commands.Bot):
    """A Bot with a built in metrics tracker that other files can access."""

    def __init__(self) -> None:
        """A Bot with a built in metrics tracker that other files can access.

        Args:
            store (YearlyMetricStore): Where to store metrics information.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)
        self.__store = YearlyMetricStore()

    @property
    def store(self) -> YearlyMetricStore:
        """Get the bot's metrics store."""
        return self.__store
