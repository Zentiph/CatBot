"""Functionality for interacting with users through the bot."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = [
    "add_new_role_to_member",
    "build_response_embed",
    "find_role",
    "get_guild_interaction_data",
    "promote_role",
    "report",
    "safe_edit",
    "safe_send",
    "update_role_color",
]

from .responses import (
    build_response_embed,
    get_guild_interaction_data,
    report,
    safe_edit,
    safe_send,
)
from .role_tools import (
    add_new_role_to_member,
    find_role,
    promote_role,
    update_role_color,
)
