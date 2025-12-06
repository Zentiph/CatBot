from typing import Final

import discord

from ..ui import DEFAULT_EMBED_COLOR
from ..ui.emoji import Status

__author__: Final[str]
__license__: Final[str]

class InvalidImageFormatError(ValueError): ...

async def report(
    interaction: discord.Interaction,
    message: str,
    status: Status,
    /,
    *,
    ephemeral: bool = True,
) -> None: ...
def generate_response_embed(
    *,
    title: str | None = None,
    description: str | None = None,
    color: int | discord.Color | None = DEFAULT_EMBED_COLOR,
    author: str | None = "CatBot",
    icon_filepath: str = "static/images/profile.jpg",
    icon_filename: str = "image.png",
) -> tuple[discord.Embed, discord.File]: ...
