from dataclasses import dataclass
from typing import Final

import discord
from discord import app_commands

__author__: Final[str]
__license__: Final[str]

@dataclass(frozen=True)
class AnimalResult:
    kind: str
    image_url: str
    fact: str | None = None
    source: str | None = None

async def fetch_inat_animal(kind: str, /) -> AnimalResult: ...
async def animal_kind_autocomplete(
    _interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]: ...
