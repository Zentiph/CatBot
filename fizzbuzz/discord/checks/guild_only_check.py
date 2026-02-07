"""Check that a command is only run in a guild."""

from typing import cast

import discord
from discord import app_commands

from ..ui.emoji import Status
from .types import Check

__author__ = "Gavin Borne"
__license__ = "MIT"


class NotInGuild(app_commands.CheckFailure):
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
def guild_only() -> Check:
    """A check that ensures a command can only be used in a guild."""

    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            raise NotInGuild()
        return True

    return app_commands.check(predicate)


def get_guild(interaction: discord.Interaction, /) -> discord.Guild:
    """Get a guild from an interaction with type safety.

    This function is only safe to use on app commands checked with guild_only().

    Args:
        interaction (discord.Interaction): The interaction instance.

    Returns:
        discord.Guild: The guild of the interaction.
    """
    return cast(discord.Guild, interaction.guild)
