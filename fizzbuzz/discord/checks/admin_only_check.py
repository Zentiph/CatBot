"""Admin-only check using DB admin roles."""

from typing import Any

import discord
from discord.ext import commands

from ...db.db import DatabaseError
from ...db.settings import settings_manager
from ..ui.emoji import Status
from .guild_only_check import NotInGuild
from .types import CheckDecorator

__author__ = "Gavin Borne"
__license__ = "MIT"


class NotAdmin(commands.CheckFailure):
    """Raised when a non-admin user attempts to use an admin-only command."""

    def __init__(self, message: str | None = None) -> None:
        """Raised when a non-admin user attempts to use an admin-only command.

        Args:
            message (str | None, optional): The error message.
                Leave as None for a default. Defaults to None.
        """
        super().__init__(
            message
            or f"{Status.FAILURE} You do not have permissions to use this command."
        )


def admin_only() -> CheckDecorator:
    """A check that ensures a command can only be used by an admin."""

    async def predicate(ctx: commands.Context[Any]) -> bool:
        member = ctx.author

        if ctx.guild is None or isinstance(member, discord.User):
            raise NotInGuild()

        if ctx.guild.owner_id == member.id:
            return True
        if member.guild_permissions.administrator:
            return True

        admin_role_ids = (
            await settings_manager.get_value("guild", ctx.guild.id, "admin_role_ids")
        ) or []
        if not isinstance(admin_role_ids, list):
            raise DatabaseError(
                "Expected a list of admin role IDs, "
                f"got {type(admin_role_ids).__name__}"
            )
        # normalize in case they were stored as strings
        admin_role_ids = (int(i) for i in admin_role_ids)

        if admin_role_ids and any(r.id in admin_role_ids for r in member.roles):
            return True

        raise NotAdmin()

    return commands.check(predicate)
