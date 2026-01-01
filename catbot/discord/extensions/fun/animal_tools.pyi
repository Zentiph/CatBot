from typing import Final

import discord

from ...ui.emoji import Visual
from ...views import RestrictedView
from .inaturalist_api import (
    AnimalResult,
)

__author__: Final[str]
__license__: Final[str]

MAX_FILENAME_LEN: Final[int]

def safe_filename(filename: str) -> str: ...
async def build_animal_embed(
    result: AnimalResult,
    description: str,
    index: int,
    cached_bytes: bytes | None = None,
) -> tuple[discord.Embed, list[discord.File]]: ...

class AnimalCarouselView(RestrictedView):
    def __init__(
        self,
        *,
        user: discord.abc.User,
        data: AnimalResult,
        embed_description: str,
        timeout: float | None = 180.0,
    ) -> None: ...
    @discord.ui.button(
        label=f"{Visual.NEXT} Next", style=discord.ButtonStyle.primary, row=0
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[AnimalCarouselView],
    ) -> None: ...
    @discord.ui.button(
        label=f"{Visual.PREVIOUS} Previous", style=discord.ButtonStyle.primary, row=0
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[AnimalCarouselView],
    ) -> None: ...
