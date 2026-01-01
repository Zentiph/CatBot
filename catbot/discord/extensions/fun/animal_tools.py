"""Tools for the /animal fun command."""

from __future__ import annotations

from io import BytesIO

import discord

from ....util.http import http_get_bytes
from ...interaction import build_response_embed, safe_edit
from ...ui.emoji import Visual
from ...views import RestrictedView
from .inaturalist_api import (
    AnimalResult,
)

__author__ = "Gavin Borne"
__license__ = "MIT"

MAX_FILENAME_LEN = 40
"""The maximum length of an attachment filename."""


def safe_filename(filename: str) -> str:
    """Ensure a filename is safe by replacing risky characters with underscores.

    Args:
        filename (str): The filename to make safe.

    Returns:
        str: The safe filename.
    """
    keep = [c.lower() if c.isalnum() else "_" for c in filename]
    out = "".join(keep).strip("_")

    return out[:MAX_FILENAME_LEN] or "animal"


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

    filename = f"{safe_filename(result.kind)}.png"
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


class AnimalCarouselView(RestrictedView):
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
        super().__init__(user=user, timeout=timeout)
        self.__data = data
        self.__urls = data.images
        self.__count = len(self.__urls)
        self.__index = 0
        self.__description = embed_description

        self.__cache: dict[int, bytes] = {}

        self.__sync_buttons()

    def __sync_buttons(self) -> None:
        self.previous_button.disabled = self.__index == 0
        self.next_button.disabled = self.__index >= self.__count - 1

    async def __render(self, interaction: discord.Interaction) -> None:
        url = self.__urls[self.__index]
        image_bytes = self.__cache.get(self.__index) or await http_get_bytes(url)
        self.__cache[self.__index] = image_bytes

        embed, files = await build_animal_embed(
            self.__data,
            self.__description,
            self.__index,
            self.__cache.get(self.__index),
        )

        self.__sync_buttons()
        await safe_edit(interaction, embed=embed, attachments=files, view=self)

    @discord.ui.button(
        label=f"{Visual.PREVIOUS} Previous", style=discord.ButtonStyle.primary, row=0
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[AnimalCarouselView],
    ) -> None:
        """Move to the previous image in the carousel.

        Supports wrapping.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        # should be disabled if it would go OOB, but clamp to be safe
        self.__index = max(0, self.__index - 1)
        await self.__render(interaction)

    @discord.ui.button(
        label=f"{Visual.NEXT} Next", style=discord.ButtonStyle.primary, row=0
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[AnimalCarouselView],
    ) -> None:
        """Move to the next image in the carousel.

        Supports wrapping.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        # should be disabled if it would go OOB, but clamp to be safe
        self.__index = min(self.__count - 1, self.__index + 1)
        await self.__render(interaction)
