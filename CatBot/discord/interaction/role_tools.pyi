# pylint:disable=all

from typing import Final

import discord

__author__: Final[str]
__license__: Final[str]

async def promote_role(role: discord.Role, /) -> None: ...
def find_role(role: str, guild: discord.Guild, /) -> discord.Role | None: ...
async def update_role_color(role: discord.Role, color: discord.Color, /) -> None: ...
async def add_new_role_to_member(
    member: discord.Member, name: str, color: discord.Color, /
) -> None: ...
