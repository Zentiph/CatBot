from abc import ABC
from collections.abc import Callable, Sequence
from typing import Final

import discord
from discord.utils import MISSING

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
    async def respond(
        self,
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
        delete_after: float = MISSING,
    ) -> None: ...
    async def edit(
        self,
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

class RestrictedModal(ABC, discord.ui.Modal):
    def __init__(self, view: RestrictedView, *, title: str) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction, /) -> bool: ...
