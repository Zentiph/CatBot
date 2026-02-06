from __future__ import annotations

from abc import abstractmethod
from typing import Final

import discord

from ..ui.emoji import Visual
from .restricted_view import RestrictedModal, RestrictedView

__author__: Final[str]
__license__: Final[str]

class PageJumpModal(RestrictedModal["CarouselView"]):
    page: discord.ui.TextInput[PageJumpModal]
    def __init__(self, view: CarouselView) -> None: ...
    async def on_submit(self, interaction: discord.Interaction, /) -> None: ...

class CarouselView(RestrictedView):
    def __init__(
        self,
        pages: int,
        *,
        user: discord.abc.User,
        timeout: float | None = 180.0,
        jump_button: bool = True,
    ) -> None: ...
    @abstractmethod
    async def render(self, interaction: discord.Interaction, /) -> None: ...
    def sync_buttons(self) -> None: ...
    @discord.ui.button(
        label=f"{Visual.PREVIOUS} Previous", style=discord.ButtonStyle.primary, row=0
    )
    async def previous_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[CarouselView]
    ) -> None: ...
    @discord.ui.button(
        label=f"{Visual.NEXT} Next", style=discord.ButtonStyle.primary, row=0
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[CarouselView],
    ) -> None: ...
    @discord.ui.button(
        label=f"{Visual.REWIND} First", style=discord.ButtonStyle.primary, row=1
    )
    async def first_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[CarouselView]
    ) -> None: ...
    @discord.ui.button(
        label=f"{Visual.FAST_FORWARD} Last", style=discord.ButtonStyle.primary, row=1
    )
    async def last_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[CarouselView],
    ) -> None: ...
    @discord.ui.button(
        label=f"{Visual.ASTERISK} Jump to page",
        style=discord.ButtonStyle.primary,
        row=2,
        disabled=True,
    )
    async def jump_to_page(
        self, interaction: discord.Interaction, _button: discord.ui.Button[CarouselView]
    ) -> None: ...
    @property
    def pages(self) -> int: ...
    @property
    def index(self) -> int: ...
    @index.setter
    def index(self, new_index: int) -> None: ...
