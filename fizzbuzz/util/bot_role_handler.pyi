import discord
from discord.ext import commands

def find_managed_bot_role_in_guild(
    bot: commands.Bot, /, guild: discord.Guild
) -> discord.Role | None: ...
def find_configurable_bot_role_in_guild(
    guild: discord.Guild,
) -> discord.Role | None: ...
async def ensure_bot_role_properties_in_guild(
    bot: commands.Bot, /, guild: discord.Guild
) -> None: ...
