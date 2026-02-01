import discord
from discord.ext import commands

def find_bot_role_in_guild(
    bot: commands.Bot, /, guild: discord.Guild
) -> discord.Role | None: ...
async def ensure_bot_role_properties_in_guild(
    bot: commands.Bot, /, guild: discord.Guild
) -> None: ...
