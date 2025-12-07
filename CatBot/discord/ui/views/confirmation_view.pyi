from __future__ import annotations

__author__: Final[str]
__license__: Final[str]

from collections.abc import Awaitable, Callable
from typing import Any, Final, TypeAlias

import discord
from discord import ui

AsyncFunction: TypeAlias = Callable[..., Awaitable[Any]]

CONFIRM_LABEL: Final[str]
DENY_LABEL: Final[str]

CONFIRM_BUTTON_STYLE: Final[discord.ButtonStyle]
DENY_BUTTON_STYLE: Final[discord.ButtonStyle]

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
    @discord.ui.button(label=CONFIRM_LABEL, style=CONFIRM_BUTTON_STYLE)
    async def confirm(
        self, interaction: discord.Interaction, button: ui.Button[ConfirmationView]
    ) -> None: ...
    @discord.ui.button(label=DENY_LABEL, style=DENY_BUTTON_STYLE)
    async def deny(
        self, interaction: discord.Interaction, button: ui.Button[ConfirmationView]
    ) -> None: ...
