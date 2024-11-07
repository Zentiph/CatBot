"""
role_manipulation.py
Role manipulation code.
"""

import logging
from typing import Sequence
import discord


async def move_role_to_top(guild: discord.Guild, role: discord.Role) -> None:
    """
    Move the role to just below the bot's highest role.

    :param guild: The guild (server) in which the role is being moved.
    :type guild: discord.Guild
    :param role: The role to move.
    :type role: discord.Role
    """

    try:
        bot_highest_role = guild.me.top_role

        if bot_highest_role.position > role.position:
            await role.edit(position=bot_highest_role.position - 1)
            logging.info(
                "Attempting to move role %s below the bot's highest role", role.name
            )

            # Refresh roles after change
            await guild.fetch_roles()  # Re-fetch roles to ensure changes are reflected
            updated_role = discord.utils.get(guild.roles, id=role.id)

            # Double-check if the role is in the correct position
            if updated_role.position == bot_highest_role.position - 1:  # type: ignore
                logging.info("Role %s is now correctly positioned", role.name)
            else:
                logging.warning(
                    "Role %s did not move to the correct position", role.name
                )
                logging.info("Retrying role movement")
                await role.edit(position=bot_highest_role.position - 1)

        else:
            logging.warning("Bot's role hierarchy prevents moving role %s", role.name)

    except discord.Forbidden:
        logging.warning("Bot lacks permissions to move roles")
    except discord.HTTPException as e:
        logging.error("Failed to move role due to an error: %s", e)


def find_existing_role(
    role: str, guild_roles: Sequence[discord.Role]
) -> discord.Role | None:
    """
    Find an existing role in a guild.

    :param role: Name of the role to find
    :type role: str
    :param guild_roles: Sequence of all roles in the guild
    :type guild_roles: Sequence[discord.Role]
    :return: The found role, or None if no role is found
    :rtype: discord.Role | None
    """

    return discord.utils.find(lambda r: r.name == role, guild_roles)


async def edit_color_role(
    role: discord.Role,
    color: discord.Color,
    user: discord.Member,
    color_repr: str | tuple[int, int, int],
) -> None:
    """
    Edit the given role to match the color and assign it to the user if necessary.

    :param role: Role to edit
    :type role: discord.Role
    :param color: New role color
    :type color: discord.Color
    :param user: User whose role to edit
    :type user: discord.Member
    :param color_repr: Representation of the color
    :type color_repr: str | tuple[int, int, int]
    """

    await role.edit(color=color)
    logging.info(
        "Role %s exists and its color has been changed to %s",
        role.name,
        color_repr,
    )

    # If the user somehow lost their role, readd it
    if role not in user.roles:
        await user.add_roles(role)


async def create_color_role(
    user: discord.Member, color: discord.Color, guild: discord.Guild
) -> None:
    """
    Create a new color role for `user` with color `color`.

    :param user: User to make the role for
    :type user: discord.Member
    :param color: Color of the role
    :type color: discord.Color
    :param guild: Guild to make the role in
    :type guild: discord.Guild
    """

    new_role = await guild.create_role(name=f"{user.name}'s Color", color=color)
    await user.add_roles(new_role)
    await move_role_to_top(guild, new_role)

    logging.info("New color role created and assigned to %s", user)
