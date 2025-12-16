from abc import ABC
from collections.abc import Callable
from typing import Final

import discord

from ..ui.emoji import Status

__author__: Final[str]
__license__: Final[str]

Check = Callable[[discord.Interaction], bool]

class RestrictedView(ABC, discord.ui.View):
    def __init__(
        self,
        *,
        user: discord.abc.User,
        timeout: float | None = 60.0,
        deny_message: str = "You can't interact with another user's embed!",
        deny_status: Status = Status.FAILURE,
        ephemeral: bool = True,
        allow: Check | None = None,
    ) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction, /) -> bool: ...

class RestrictedModal(ABC, discord.ui.Modal):
    def __init__(self, view: RestrictedView, *, title: str) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction, /) -> bool: ...
