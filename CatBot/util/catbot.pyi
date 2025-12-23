from typing import Final

from discord.ext import commands

from ..db.cat_scan import YearlyMetricStore

__author__: Final[str]
__license__: Final[str]

class CatBot(commands.Bot):
    def __init__(self) -> None: ...
    @property
    def store(self) -> YearlyMetricStore: ...
