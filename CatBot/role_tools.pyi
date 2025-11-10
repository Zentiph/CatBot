# pylint:disable=all

from typing import Final
import discord

__author__: Final[str]
__license__: Final[str]

async def promote_role(role: discord.Role) -> None: ...
def find_role(role: str, guild: discord.Guild) -> discord.Role | None: ...
