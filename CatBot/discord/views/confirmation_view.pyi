from __future__ import annotations

__author__: Final[str]
__license__: Final[str]

from collections.abc import Awaitable, Callable
from typing import Any, Final, TypeAlias

import discord
from discord import ui

AsyncFunction: TypeAlias = Callable[..., Awaitable[Any]]

class ConfirmationView(ui.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        /,
        *,
        confirmation_message: str,
        denial_message: str,
    ) -> None: ...
    def on_confirmation(
        self,
        func: AsyncFunction | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None: ...
    def on_denial(
        self,
        func: AsyncFunction | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None: ...
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: ui.Button[ConfirmationView]
    ) -> None: ...
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def deny(
        self, interaction: discord.Interaction, button: ui.Button[ConfirmationView]
    ) -> None: ...
