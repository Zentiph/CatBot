from typing import Final

from discord.ext import commands

from .types import CheckDecorator

__author__: Final[str]
__license__: Final[str]

class NotAdmin(commands.CheckFailure):
    def __init__(self, message: str | None = None) -> None: ...

def admin_only() -> CheckDecorator: ...
