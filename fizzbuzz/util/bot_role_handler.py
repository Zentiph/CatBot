"""Tools for handling the bot's managed role in each guild."""

import logging

import discord
from discord.ext import commands

from ..discord.ui.constants import DEFAULT_EMBED_COLOR

_CONFIG_ROLE_NAME = "FizzBuzz (managed by FB)"


def find_managed_bot_role_in_guild(
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


def find_configurable_bot_role_in_guild(guild: discord.Guild) -> discord.Role | None:
    """Get the bot's configurable role in a guild.

    This role may exist because it was created as a fallback if
    the bot attempted to edit its managed role but could not.

    Args:
        guild (discord.Guild): The guild to search in.

    Returns:
        discord.Role | None: The bot's configurable role, if it exists.
    """
    for role in guild.roles:
        if role.name == _CONFIG_ROLE_NAME:
            return role

    return None


async def _create_configurable_bot_role(guild: discord.Guild) -> bool:
    if not guild.me.guild_permissions.manage_roles:
        return False

    try:
        # TODO: eventually store in DB for easy re-access
        role = await guild.create_role(
            reason="Configurable role for FizzBuzz",
            name=_CONFIG_ROLE_NAME,
            color=DEFAULT_EMBED_COLOR,
        )
        await role.move(below=guild.me.top_role)
    except discord.HTTPException as e:  # likely missing permissions, log just in case
        logging.exception(
            f"Bad HTTP code when attempting to edit bot's config role (code {e.code})"
        )
        return False
    else:
        return True


async def _edit_bot_role(
    bot: commands.Bot, role: discord.Role, *, config_role: bool
) -> None:
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

    name_to_match = _CONFIG_ROLE_NAME if config_role else bot_user.name
    if role.name != name_to_match:
        try:
            await role.edit(name=name_to_match)
        except discord.Forbidden:
            logging.debug("Missing permission to edit role name")
        except discord.HTTPException:
            logging.exception("Discord API error")


async def ensure_bot_role_properties_in_guild(
    bot: commands.Bot, /, guild: discord.Guild
) -> None:
    """Ensure the bot's managed role's properties are correctly set in a guild.

    Args:
        bot (commands.Bot): The bot.
        guild (discord.Guild): The guild to set the color in.
    """
    # first try to edit the bot's role directly
    if guild.me.guild_permissions.manage_roles:
        role = find_managed_bot_role_in_guild(bot, guild)
        if role is not None and role.is_assignable() and not role.is_default():
            await _edit_bot_role(bot, role, config_role=False)
            return

    # otherwise find/make a configurable role
    role = find_configurable_bot_role_in_guild(guild)
    if role is not None:
        await _edit_bot_role(bot, role, config_role=True)

    if not await _create_configurable_bot_role(guild):
        logging.warning(
            "Bot was unable to ensure its role properties "
            f"in guild {guild.name} (id: {guild.id})"
        )
