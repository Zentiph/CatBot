"""Role manipulation tools."""

import logging

import discord

__author__ = "Gavin Borne"
__license__ = "MIT"

from ..info import BOT_APP_ID


async def promote_role(role: discord.Role, /) -> None:
    """Promote the role as high as possible.

    Args:
        role (discord.Role): The role to move.
    """
    guild = role.guild
    try:
        bot_highest_role = (guild.me or await guild.fetch_member(BOT_APP_ID)).top_role
        if bot_highest_role.position > role.position:
            await role.edit(position=bot_highest_role.position - 1)
            logging.debug(
                "Attempting to move role %s below the bot's highest role", role.name
            )

            # refresh roles after change
            await guild.fetch_roles()
            updated_role = discord.utils.get(guild.roles, id=role.id)
            if updated_role is None:
                logging.error(
                    "No roles under bot role after moving role to below bot role"
                )
                return

            # double-check correct position
            if updated_role.position == bot_highest_role.position - 1:
                logging.debug("Role %s is now correctly positioned", role.name)
            else:
                logging.warning(
                    "Role %s did not move to the correct position, retrying...",
                    role.name,
                )
                await role.edit(position=bot_highest_role.position - 1)

        else:
            logging.warning("Bot's role hierarchy prevents moving role %s", role.name)

    except discord.Forbidden:
        logging.warning("Bot lacks permissions to move color")
    except discord.HTTPException as e:
        logging.error("Failed to move role due to an error: %s", e, exc_info=True)


def find_role(role: str, guild: discord.Guild, /) -> discord.Role | None:
    """Find an role in a guild.

    Args:
        role (str): The name of the role to find.
        guild (discord.Guild): The guild to search in.

    Returns:
        discord.Role | None: The role, if it exists, otherwise None.
    """
    return discord.utils.find(lambda r: r.name == role, guild.roles)


async def update_role_color(role: discord.Role, color: discord.Color, /) -> None:
    """Update the given role's color.

    Args:
        role (discord.Role): The role to edit.
        color (discord.Color): The new color.
    """
    await role.edit(color=color)
    logging.debug(
        "Role %s has had its color changed to %r",
        role.name,
        (color.r, color.g, color.b),
    )


async def add_new_role_to_member(
    member: discord.Member, name: str, color: discord.Color, /
) -> None:
    """Create a new role and give it to the member.

    Args:
        member (discord.Member): The member to give the role to.
        name (str): The name of the role.
        color (discord.Color): The color of the role.
    """
    new_role = await member.guild.create_role(name=name, color=color)
    await member.add_roles(new_role)
    await promote_role(new_role)

    logging.debug("New role %s created and assigned to %s", name, member)
