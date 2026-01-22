from abc import abstractmethod
from typing import Final

import discord

from ..ui.emoji import Visual
from .restricted_view import RestrictedView

__author__: Final[str]
__license__: Final[str]

class CarouselView(RestrictedView):
    def __init__(
        self, pages: int, *, user: discord.abc.User, timeout: float | None = 180.0
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
    @property
    def pages(self) -> int: ...
    @property
    def index(self) -> int: ...
