"""A carousel view that can move between pages with buttons."""

from __future__ import annotations

from abc import abstractmethod

import discord

from ..ui.emoji import Visual
from .restricted_view import RestrictedView

__author__ = "Gavin Borne"
__license__ = "MIT"


class CarouselView(RestrictedView):
    """A carousel view that can move between pages with buttons."""

    def __init__(
        self, pages: int, *, user: discord.abc.User, timeout: float | None = 180.0
    ) -> None:
        """A carousel view that can move between pages with buttons.

        Args:
            pages (int): The number of pages in the view.
            user (discord.abc.User): The user who initiated the view.
            timeout (float | None, optional): The timeout of the view (in seconds).
                Defaults to 180.0.
        """
        super().__init__(user=user, timeout=timeout)
        self.__count = pages
        self.__index = 0

        self.sync_buttons()

    @abstractmethod
    async def render(self, interaction: discord.Interaction, /) -> None:
        """Render the view after a button is pressed.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        ...

    def sync_buttons(self) -> None:
        """Sync the buttons of the view.

        The previous button is disabled if the view is at the leftmost page.
        The next button is disabled if the view is at the rightmost page.
        """
        self.previous_button.disabled = self.__index == 0
        self.next_button.disabled = self.__index >= self.__count - 1

    @discord.ui.button(
        label=f"{Visual.PREVIOUS} Previous", style=discord.ButtonStyle.primary, row=0
    )
    async def previous_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[CarouselView]
    ) -> None:
        """Move to the previous image in the carousel.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        # should be disabled if it would go OOB, but clamp to be safe
        self.__index = max(0, self.__index - 1)
        await self.render(interaction)

    @discord.ui.button(
        label=f"{Visual.NEXT} Next", style=discord.ButtonStyle.primary, row=0
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[CarouselView],
    ) -> None:
        """Move to the next image in the carousel.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        # should be disabled if it would go OOB, but clamp to be safe
        self.__index = min(self.__count - 1, self.__index + 1)
        await self.render(interaction)

    @property
    def pages(self) -> int:
        """Get the number of pages of this carousel view.

        Returns:
            int: The number of pages in the view.
        """
        return self.__count

    @property
    def index(self) -> int:
        """Get the current page index of this carousel view.

        Returns:
            int: The current page index of the view.
        """
        return self.__index
