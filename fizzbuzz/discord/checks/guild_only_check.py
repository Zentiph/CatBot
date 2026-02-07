"""Check that a command is only run in a guild."""

from typing import Any

from discord.ext import commands

from ..ui.emoji import Status
from .types import CheckDecorator

__author__ = "Gavin Borne"
__license__ = "MIT"


class NotInGuild(commands.CheckFailure):
    """Raised when a user who is not in a guild attempts to use a guild-only command."""

    def __init__(self, message: str | None = None) -> None:
        """Raised when a user not in a guild attempts to use a guild-only command.

        Args:
            message (str | None, optional): The error message.
                Leave as None for a default. Defaults to None.
        """
        super().__init__(
            message or f"{Status.FAILURE} You must be in a guild to use this command."
        )


# while this does exist already, I'm opting to do my own here for
# more customized handling and error reporting.
def guild_only() -> CheckDecorator:
    """A check that ensures a command can only be used in a guild."""

    def predicate(ctx: commands.Context[Any]) -> bool:
        if ctx.guild is None:
            raise NotInGuild()
        return True

    return commands.check(predicate)
