from abc import ABC
from typing import Final

import discord

__author__: Final[str]
__license__: Final[str]

class RestrictedView(ABC, discord.ui.View):
    def __init__(
        self, *, user: discord.abc.User, timeout: float | None = 60.0
    ) -> None: ...
    async def validate_user(self, interaction: discord.Interaction, /) -> bool: ...
