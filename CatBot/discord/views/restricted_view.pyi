from abc import ABC
from collections.abc import Callable, Sequence
from typing import Final, Generic, TypeVar

import discord
from discord.utils import MISSING

from ..ui.emoji import Status

__author__: Final[str]
__license__: Final[str]

RV = TypeVar("RV", bound="RestrictedView")

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
    async def send(
        self,
        interaction: discord.Interaction,
        /,
        *,
        content: str | None = None,
        ephemeral: bool = True,
        embed: discord.Embed = MISSING,
        embeds: Sequence[discord.Embed] = MISSING,
        files: Sequence[discord.File] = MISSING,
    ) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction, /) -> bool: ...

class RestrictedModal(Generic[RV], ABC, discord.ui.Modal):
    def __init__(self, view: RV, /, *, title: str) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction, /) -> bool: ...
    @property
    def view(self) -> RV: ...
