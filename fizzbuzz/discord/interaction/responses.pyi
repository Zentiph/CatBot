from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

import discord
from discord.utils import MISSING

from ..ui import DEFAULT_EMBED_COLOR
from ..ui.emoji import Status

__author__: Final[str]
__license__: Final[str]

@dataclass(frozen=True)
class GuildInteractionData:
    member: discord.Member
    guild: discord.Guild

class InvalidImageFormatError(ValueError): ...

async def safe_send(
    interaction: discord.Interaction,
    /,
    content: str | None = None,
    *,
    ephemeral: bool = True,
    embed: discord.Embed = MISSING,
    embeds: Sequence[discord.Embed] = MISSING,
    view: discord.ui.View = MISSING,
    file: discord.File = MISSING,
    files: Sequence[discord.File] = MISSING,
    delete_after: float | None = None,
) -> discord.Message | None: ...
async def safe_edit(
    interaction: discord.Interaction,
    /,
    *,
    content: str | None = None,
    embed: discord.Embed = MISSING,
    embeds: Sequence[discord.Embed] = MISSING,
    attachments: Sequence[discord.Attachment | discord.File] = MISSING,
    view: discord.ui.View = MISSING,
    allowed_mentions: discord.AllowedMentions = MISSING,
) -> None: ...
async def report(
    interaction: discord.Interaction,
    message: str,
    status: Status,
    /,
    *,
    ephemeral: bool = True,
) -> None: ...
def build_response_embed(
    *,
    title: str | None = None,
    description: str | None = None,
    color: int | discord.Color | None = DEFAULT_EMBED_COLOR,
    author: str | None = "FizzBuzz",
    icon_filepath: str = "static/branding/fizzbuzz_icon.jpg",
    icon_filename: str = "image.png",
) -> tuple[discord.Embed, discord.File]: ...
