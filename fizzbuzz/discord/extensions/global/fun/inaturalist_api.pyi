from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

import discord
from discord import app_commands

__author__: Final[str]
__license__: Final[str]

ImageFetchAmount: TypeAlias = Literal[1, 2, 3, 4, 5]

@dataclass(frozen=True)
class AnimalResult:
    kind: str
    image_url: str
    images: list[str]
    fact: str | None = None
    source: str | None = None

async def fetch_inat_animal(kind: str, /, *, images: int = 1) -> AnimalResult: ...
async def animal_kind_autocomplete(
    _interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]: ...
