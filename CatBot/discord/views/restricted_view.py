"""A restricted ui View that only the interaction user can interact with."""

from abc import ABC
from collections.abc import Callable

import discord

from ..interaction import report
from ..ui.emoji import Status

__author__ = "Gavin Borne"
__license__ = "MIT"

Check = Callable[[discord.Interaction], bool]


class RestrictedView(ABC, discord.ui.View):
    """A view that restricts people except the interaction user from using it."""

    def __init__(
        self,
        *,
        user: discord.abc.User,
        timeout: float | None = 60.0,
        deny_message: str = "You can't interact with another user's embed!",
        deny_status: Status = Status.FAILURE,
        ephemeral: bool = True,
        allow: Check | None = None,
    ) -> None:
        """A view that restricts people except the interaction user from using it.

        Args:
            user (discord.abc.User): The user with interaction access.
            timeout (float | None, optional): The timeout of the view (in seconds).
                Defaults to 60.0.
            deny_message (str, optional): The message to give when denying access to
                unauthorized users. Defaults to "You can't interact with another user's
                embed!"
            deny_status (Status, optional): The response status to give when denying
                access to unauthorized users.
            ephemeral (bool, optional): Whether the deny response should be ephemeral.
                Defaults to True.
            allow (Check | None, optional): An optional predicate to allow additional
                users to interact with the view. Defaults to None.
        """
        super().__init__(timeout=timeout)
        self.__user_id = user.id
        self.__deny_message = deny_message
        self.__deny_status = deny_status
        self.__deny_ephemeral = ephemeral
        self.__allow = allow

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        """On each interaction instance, check that the user is authorized.

        Args:
            interaction (discord.Interaction): The interaction instance.

        Returns:
            bool: Whether the user who interacted is authorized to interact with this
                view.
        """
        ok_owner = interaction.user.id == self.__user_id
        ok_extra = self.__allow(interaction) if self.__allow else False

        if not (ok_owner or ok_extra):
            await report(
                interaction,
                self.__deny_message,
                self.__deny_status,
                ephemeral=self.__deny_ephemeral,
            )
            return False
        return True


class RestrictedModal(ABC, discord.ui.Modal):
    """A modal that restricts people except the interaction user from using it."""

    def __init__(self, view: RestrictedView, *, title: str) -> None:
        """A modal that restricts people except the interaction user from using it.

        Args:
            view (RestrictedView): The restricted view which this modal is part of.
            title (str): The title of the modal.
        """
        super().__init__(title=title)
        self.__view = view

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        """Validate that the user from the interaction is this embed's user.

        Args:
            interaction (discord.Interaction): The interaction instance.

        Returns:
            bool: Whether this user is validated.
        """
        return await self.__view.interaction_check(interaction)
