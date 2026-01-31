from typing import Final

import discord

from ...views import CarouselView
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

class AnimalCarouselView(CarouselView):
    def __init__(
        self,
        *,
        user: discord.abc.User,
        data: AnimalResult,
        embed_description: str,
        timeout: float | None = 180.0,
    ) -> None: ...
    async def render(self, interaction: discord.Interaction) -> None: ...
