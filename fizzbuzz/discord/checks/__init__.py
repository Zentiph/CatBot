"""A collection of custom checks to use for commands."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = [
    "NotAdmin",
    "NotInGuild",
    "admin_only",
    "get_guild",
    "get_member",
    "guild_only",
]

from .admin_only_check import NotAdmin, admin_only
from .guild_only_check import NotInGuild, get_guild, get_member, guild_only
