"""A carousel view that can move between pages with buttons."""

from __future__ import annotations

from abc import abstractmethod

import discord

from ..interaction import report
from ..ui.emoji import Status, Visual
from .restricted_view import RestrictedModal, RestrictedView

__author__ = "Gavin Borne"
__license__ = "MIT"


class PageJumpModal(RestrictedModal["CarouselView"]):
    """A modal that takes a page number to jump to in a CarouselView."""

    # THIS NEEDS TO UPDATED WITH CarouselView's PAGE COUNT IN __init__
    page: discord.ui.TextInput[PageJumpModal] = discord.ui.TextInput(
        label="Page number", placeholder="", min_length=1
    )

    def __init__(self, view: CarouselView) -> None:
        """A modal that takes a page number to jump to in a CarouselView.

        Args:
            view (CarouselView): The view that this modal spawned from.
        """
        super().__init__(view, title="Jump to Page")
        self.page.label = f"Page number (1-{view.pages})"
        self.page.placeholder = "2"

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        """On user-submission, validate the page number and apply it if possible.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        try:
            page = int(str(self.page))
        except ValueError:
            await report(
                interaction, "Please enter a valid page number.", Status.FAILURE
            )
            return

        if page < 1 or page > self.view.pages:
            await report(interaction, "Invalid page number!", Status.FAILURE)
            return

        self.view.index = page - 1
        await self.view.render(interaction)


class CarouselView(RestrictedView):
    """A carousel view that can move between pages with buttons."""

    def __init__(
        self,
        pages: int,
        *,
        user: discord.abc.User,
        timeout: float | None = 180.0,
        jump_button: bool = True,
    ) -> None:
        """A carousel view that can move between pages with buttons.

        Args:
            pages (int): The number of pages in the view.
            user (discord.abc.User): The user who initiated the view.
            timeout (float | None, optional): The timeout of the view (in seconds).
                Defaults to 180.0.
            jump_button (bool, optional): Whether to include a "Jump to page" button
                that users can press to go to a specific page number. Defaults to True.
        """
        super().__init__(user=user, timeout=timeout)
        self.__count = pages
        self.__index = 0
        self.jump_to_page.disabled = not jump_button

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

    @discord.ui.button(
        label=f"{Visual.ASTERISK} Jump to page",
        style=discord.ButtonStyle.primary,
        row=1,
        disabled=True,  # will be set in the constructor
    )
    async def jump_to_page(
        self, interaction: discord.Interaction, _button: discord.ui.Button[CarouselView]
    ) -> None:
        """Jump to a specific page via a modal.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        await interaction.response.send_modal(PageJumpModal(self))

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

    @index.setter
    def index(self, new_index: int) -> None:
        """Set the current page index of this carousel view.

        Args:
            new_index (int): The new index.
        """
        if new_index < 0 or new_index > self.pages:
            raise ValueError("Invalid page number")

        self.__index = new_index
