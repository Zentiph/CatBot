"""A collection of custom checks to use for commands."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = [
    "NotInGuild",
    "Unauthorized",
    "admin_only",
    "get_guild",
    "get_member",
    "guild_only",
    "owner_only",
]

from .admin_checks import Unauthorized, admin_only, owner_only
from .guild_checks import NotInGuild, get_guild, get_member, guild_only
