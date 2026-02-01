"""Tools for handling the bot's managed role in each guild."""

import logging

import discord
from discord.ext import commands

from ..discord.ui.constants import DEFAULT_EMBED_COLOR


def find_bot_role_in_guild(
    bot: commands.Bot, /, guild: discord.Guild
) -> discord.Role | None:
    """Get the bot's managed role in a guild.

    Args:
        bot (commands.Bot): The bot to find the managed role of.
        guild (discord.Guild): The guild to search in.

    Returns:
        discord.Role | None: The bot's managed role, if it could be found.
    """
    for role in guild.roles:
        tags = getattr(role, "tags", None)
        if tags is None:
            continue

        bot_id = getattr(tags, "bot_id", None)
        bot_user_id = bot.user.id if bot.user is not None else None
        if bot_user_id and bot_id == bot_user_id:
            return role

    return None


async def ensure_bot_role_properties_in_guild(
    bot: commands.Bot, /, guild: discord.Guild
) -> None:
    """Ensure the bot's managed role's properties are correctly set in a guild.

    Args:
        bot (commands.Bot): The bot.
        guild (discord.Guild): The guild to set the color in.
    """
    role = find_bot_role_in_guild(bot, guild)
    if role is None:
        return

    if role.color != DEFAULT_EMBED_COLOR:
        try:
            await role.edit(color=DEFAULT_EMBED_COLOR)
        except discord.Forbidden:
            logging.debug("Missing permission to set role color")
        except discord.HTTPException:
            logging.exception("Discord API error")

    bot_user = bot.user
    if bot_user is None:
        return

    if role.name != bot_user.name:
        await role.edit(name=bot_user.name)
