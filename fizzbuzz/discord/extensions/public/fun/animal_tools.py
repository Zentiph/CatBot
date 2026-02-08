"""Tools for the /animal fun command."""

from __future__ import annotations

from io import BytesIO

import discord

from .....util.http import http_get_bytes
from ....interaction import build_response_embed, safe_edit
from ....ui.emoji import Visual
from ....views import CarouselView
from .inaturalist_api import (
    AnimalResult,
)

__author__ = "Gavin Borne"
__license__ = "MIT"

_MAX_FILENAME_LEN = 40  # maximum length of an attachment filename


def _safe_filename(filename: str) -> str:
    # ensure a filename is safe by replacing risky characters with underscores
    keep = [c.lower() if c.isalnum() else "_" for c in filename]
    out = "".join(keep).strip("_")

    return out[:_MAX_FILENAME_LEN] or "animal"


async def build_animal_embed(
    result: AnimalResult,
    description: str,
    index: int,
    cached_bytes: bytes | None = None,
) -> tuple[discord.Embed, list[discord.File]]:
    """Build an animal embed (for /animal).

    Args:
        result (AnimalResult): The animal result from talking to iNaturalist.
        description (str): The description of the embed.
        index (int): The index of which image in the carousel this embed is made for.
        cached_bytes (bytes | None, optional): The cached image bytes to use.
            Defaults to None.

    Returns:
        tuple[discord.Embed, list[discord.File]]: The embed and its files.
    """
    if cached_bytes:
        image_fp = BytesIO(cached_bytes)
    else:
        image_bytes = await http_get_bytes(result.images[index], timeout=10)
        image_fp = BytesIO(image_bytes)

    filename = f"{_safe_filename(result.kind)}.png"
    file = discord.File(fp=image_fp, filename=filename)

    description_parts = []
    if result.fact:
        description_parts.append(result.fact)
    if result.source:
        description_parts.append(f"*Source: {result.source}*")

    embed, icon = build_response_embed(
        title=f"{Visual.PAWS} Random {result.kind.title()}"
        f" ({index + 1}/{len(result.images) if result.images else 0})",
        description=description,
    )
    embed.set_image(url=f"attachment://{filename}")

    return embed, [file, icon]


class AnimalCarouselView(CarouselView):
    """An animal image carousel view."""

    def __init__(
        self,
        *,
        user: discord.abc.User,
        data: AnimalResult,
        embed_description: str,
        timeout: float | None = 180.0,
    ) -> None:
        """An animal image carousel view.

        Args:
            user (discord.abc.User): The user who spawned the view.
            data (AnimalResult): The animal data obtained.
            embed_description(str): The description of the embed.
            timeout (float | None, optional): The timeout of the view in seconds.
                Defaults to 180.0.
        """
        self.__data = data
        self.__urls = data.images
        self.__description = embed_description
        self.__cache: dict[int, bytes] = {}

        super().__init__(len(self.__urls), user=user, timeout=timeout)

    async def render(self, interaction: discord.Interaction, /) -> None:
        """Render the next page and image after a button is pressed.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        url = self.__urls[self.index]
        image_bytes = self.__cache.get(self.index) or await http_get_bytes(url)
        self.__cache[self.index] = image_bytes

        embed, files = await build_animal_embed(
            self.__data,
            self.__description,
            self.index,
            self.__cache.get(self.index),
        )

        self.sync_buttons()
        await safe_edit(interaction, embed=embed, attachments=files, view=self)
