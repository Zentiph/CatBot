"""Check that a command is only run in a guild."""

from typing import Final

import discord
from discord import app_commands

from .types import Check

__author__: Final[str]
__license__: Final[str]

class NotInGuild(app_commands.CheckFailure):
    def __init__(self, message: str | None = None) -> None: ...

def guild_only() -> Check: ...
def get_guild(interaction: discord.Interaction, /) -> discord.Guild: ...
def get_member(interaction: discord.Interaction, /) -> discord.Member: ...
