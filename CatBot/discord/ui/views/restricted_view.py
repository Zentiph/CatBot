"""A restricted ui View that only the interaction user can interact with."""

from abc import ABC

import discord

from ...interaction import report
from ..emoji import Status

__author__ = "Gavin Borne"
__license__ = "MIT"


class RestrictedView(ABC, discord.ui.View):
    """A view that restricts people except the interaction user from using it."""

    def __init__(self, *, user: discord.abc.User, timeout: float | None = 60.0) -> None:
        """A view that restricts people except the interaction user from using it.

        Args:
            user (discord.abc.User): The user with interaction access.
            timeout (float | None, optional): The timeout of the view (in seconds).
                Defaults to 60.0.
        """
        super().__init__(timeout=timeout)
        self.__user_id = user.id

    async def validate_user(self, interaction: discord.Interaction, /) -> bool:
        """Validate that the user from the interaction is this embed's user.

        Args:
            interaction (discord.Interaction): The interaction instance.

        Returns:
            bool: Whether this user is validated.
        """
        if interaction.user.id != self.__user_id:
            await report(
                interaction,
                "You can't interact with another user's embed!",
                Status.FAILURE,
            )
            return False
        return True
