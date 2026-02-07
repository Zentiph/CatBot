from __future__ import annotations

import logging
from typing import Final

import discord

from ....views import RestrictedModal, RestrictedView
from .color_tools import Color3

__author__: Final[str]
__license__: Final[str]

def build_color_embed(
    *, title: str, description: str, color: Color3
) -> tuple[discord.Embed, list[discord.File]]: ...
def get_color_role_name(member: discord.Member, /) -> str: ...
async def update_color_role(
    member: discord.Member,
    guild: discord.Guild,
    color: discord.Color,
    color_repr: str,
    interaction: discord.Interaction,
    logger: logging.Logger,
) -> None: ...

class LightenModal(RestrictedModal["ColorView"]):
    amount: Final[discord.ui.TextInput[LightenModal]]
    def __init__(self, view: ColorView) -> None: ...
    async def on_submit(self, interaction: discord.Interaction, /) -> None: ...

class DarkenModal(RestrictedModal["ColorView"]):
    amount: Final[discord.ui.TextInput[DarkenModal]]
    def __init__(self, view: ColorView) -> None: ...
    async def on_submit(self, interaction: discord.Interaction, /) -> None: ...

class ColorView(RestrictedView):
    def __init__(
        self,
        user: discord.abc.User,
        /,
        *,
        color: Color3,
        timeout: float | None = 60.0,
        in_server: bool,
    ) -> None: ...
    @discord.ui.button(label="Invert", style=discord.ButtonStyle.primary, row=0)
    async def invert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None: ...
    @discord.ui.button(label="Lighten", style=discord.ButtonStyle.primary, row=1)
    async def lighten_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None: ...
    @discord.ui.button(label="Darken", style=discord.ButtonStyle.primary, row=1)
    async def darken_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None: ...
    @discord.ui.button(
        label="Set As Color Role",
        style=discord.ButtonStyle.primary,
        row=2,
        disabled=True,
        custom_id="color:set_role",
    )
    async def set_as_role(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None: ...
    @discord.ui.button(label="Revert", style=discord.ButtonStyle.secondary, row=2)
    async def revert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None: ...
