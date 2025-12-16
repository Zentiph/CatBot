"""A restricted ui View that only the interaction user can interact with."""

from abc import ABC
from collections.abc import Callable, Sequence
import contextlib
from typing import Generic, Protocol, TypeVar, runtime_checkable

import discord
from discord.utils import MISSING

from ..interaction import report, safe_send
from ..ui.emoji import Status

__author__ = "Gavin Borne"
__license__ = "MIT"

RV = TypeVar("RV", bound="RestrictedView")

Check = Callable[[discord.Interaction], bool]


@runtime_checkable
class SupportsDisabled(Protocol):
    """An instance that has a "disabled" attribute."""

    disabled: bool


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
        remove_on_timeout: bool = False,
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
            remove_on_timeout (boolean, optional): Whether to remove buttons on timeout.
                Defaults to False.
        """
        super().__init__(timeout=timeout)
        self.__user_id = user.id
        self.__deny_message = deny_message
        self.__deny_status = deny_status
        self.__deny_ephemeral = ephemeral
        self.__allow = allow
        self.__message: discord.Message | None = None
        self.__remove_on_timeout = remove_on_timeout

    async def send(
        self,
        interaction: discord.Interaction,
        /,
        *,
        content: str | None = None,
        ephemeral: bool = True,
        embed: discord.Embed = MISSING,
        embeds: Sequence[discord.Embed] = MISSING,
        file: discord.File = MISSING,
        files: Sequence[discord.File] = MISSING,
    ) -> None:
        """Send this view in a message.

        Also attempt to bind that message so this view can remove its buttons when the
        timeout ends.

        Args:
            interaction (discord.Interaction): The interaction instance to respond to.
            content (str | None, optional): The message content. If None, content is
                omitted for followup sends. Defaults to None.
            ephemeral (bool, optional): Whether the message should be ephemeral.
                Defaults to True.
            embed (discord.Embed, optional): A single embed to include. Defaults to
                `MISSING`.
            embeds (Sequence[discord.Embed], optional): Multiple embeds to include.
                Defaults to `MISSING`.
            file (discord.File, optional): A single file to include. Defaults to
                `MISSING`.
            files (Sequence[discord.File], optional): Multiple files to include.
                Defaults to `MISSING`.
        """
        self.__message = await safe_send(
            interaction,
            content,
            ephemeral=ephemeral,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            view=self,
        )

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

    async def on_timeout(self) -> None:
        """Disable UI components when the view times out."""
        if self.__remove_on_timeout:
            if self.__message is not None:
                with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                    await self.__message.edit(view=None)
            return

        for item in self.children:
            if isinstance(item, SupportsDisabled):
                item.disabled = True

        if self.__message is not None:
            with contextlib.suppress(discord.HTTPException, discord.Forbidden):
                await self.__message.edit(view=self)


class RestrictedModal(ABC, discord.ui.Modal, Generic[RV]):
    """A modal that restricts people except the interaction user from using it."""

    def __init__(self, view: RV, /, *, title: str) -> None:
        """A modal that restricts people except the interaction user from using it.

        Args:
            view (RV): The restricted view which this modal is part of.
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

    @property
    def view(self) -> RV:
        """Get this modal's view."""
        return self.__view
