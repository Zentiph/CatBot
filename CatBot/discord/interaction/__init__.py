"""Functionality for interacting with users through the bot."""

__author__ = "Gavin Borne"
__license__ = "MIT"

__all__ = [
    "add_new_role_to_member",
    "find_role",
    "generate_response_embed",
    "promote_role",
    "report",
    "update_role_color",
]

from .responses import generate_response_embed, report
from .role_tools import (
    add_new_role_to_member,
    find_role,
    promote_role,
    update_role_color,
)
