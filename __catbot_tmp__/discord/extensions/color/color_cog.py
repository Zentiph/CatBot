"""Color tools and color role assignment commands."""

# TODO implement more color info stuff for Color3 methods
# like relative luminance and hsl
# TODO color palette generator

from __future__ import annotations

import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from ....util.pawprints import cog_setup_log_msg, log_app_command
from ...interaction import (
    build_response_embed,
    find_role,
    get_guild_interaction_data,
    report,
    safe_send,
)
from ...ui.emoji import Status, Visual
from .color_tools import (
    CSS_BLUES,
    CSS_BROWNS,
    CSS_COLOR_NAME_TO_HEX,
    CSS_GRAYS,
    CSS_GREENS,
    CSS_ORANGES,
    CSS_PINKS,
    CSS_PURPLES,
    CSS_REDS,
    CSS_WHITES,
    CSS_YELLOWS,
    Color3,
)
from .color_ui import (
    ColorView,
    build_color_embed,
    get_color_role_name,
    update_color_role,
)

__author__ = "Gavin Borne"
__license__ = "MIT"

logger = logging.getLogger("ColorCog")

ColorRoleAction = Literal["set", "reset", "reassign"]
ColorRoleKind = Literal["hex", "rgb", "name", "random", "copy"]
ColorKind = Literal["hex", "rgb", "name", "role", "random"]


async def _handle_colorrole_set(
    interaction: discord.Interaction,
    member: discord.Member,
    guild: discord.Guild,
    kind: ColorRoleKind,
    hex6: str | None = None,
    r: int | None = None,
    g: int | None = None,
    b: int | None = None,
    name: str | None = None,
    role: discord.Role | None = None,
) -> None:
    if kind == "hex":
        if not hex6 or not Color3.validate_hex(hex6):
            await report(interaction, "Provide a valid hex color.", Status.FAILURE)
            return
        hex_norm = hex6.lstrip("#").lower()
        discord_color = discord.Color(int(hex_norm, 16))
        color_repr = f"#{hex_norm}"

    elif kind == "rgb":
        if r is None or g is None or b is None or not Color3.validate_rgb(r, g, b):
            await report(
                interaction, "Provide a valid RGB color (0-255).", Status.FAILURE
            )
            return
        discord_color = discord.Color.from_rgb(r, g, b)
        color_repr = str((r, g, b))

    elif kind == "name":
        if not name:
            await report(interaction, "Provide a CSS color name.", Status.FAILURE)
            return
        key = name.lower()
        if key not in CSS_COLOR_NAME_TO_HEX:
            await report(
                interaction, "Unknown color name. Use /color list.", Status.FAILURE
            )
            return
        discord_color = discord.Color(int(CSS_COLOR_NAME_TO_HEX[key], 16))
        color_repr = key

    elif kind == "copy":
        if role is None:
            await report(interaction, "Provide a role to copy.", Status.FAILURE)
            return
        discord_color = role.color
        color_repr = f"{discord_color.to_rgb()!s} (copied from {role.name})"

    else:  # random
        discord_color = Color3.random().as_discord_color()
        color_repr = f"{discord_color.to_rgb()!s} (random)"

    await update_color_role(
        member, guild, discord_color, color_repr, interaction, logger
    )


class ColorCog(commands.Cog, name="Color Role Commands"):
    """Cog containing color role commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create the ColorCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(name="colorrole", description="Manage your custom color role")
    @app_commands.describe(
        action="What to do",
        kind="How to pick the color (only for action=set)",
        hex6="Hex value (RRGGBB or #RRGGBB)",
        r="Red (0-255)",
        g="Green (0-255)",
        b="Blue (0-255)",
        name="CSS color name",
        role="Role to copy the color from",
    )
    async def colorrole(
        self,
        interaction: discord.Interaction,
        action: ColorRoleAction,
        kind: ColorRoleKind | None = None,
        hex6: str | None = None,
        r: int | None = None,
        g: int | None = None,
        b: int | None = None,
        name: str | None = None,
        role: discord.Role | None = None,
    ) -> None:
        """Color role command handler."""
        log_app_command(interaction)

        # all colorrole actions require a guild + Member
        data = get_guild_interaction_data(interaction)
        if data is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        member = data.member
        guild = data.guild

        if action == "reset":
            existing_role = find_role(get_color_role_name(member), guild)
            if not existing_role:
                await report(
                    interaction, "You do not have a color role!", Status.FAILURE
                )
                return
            await existing_role.edit(color=discord.Color(int("000000", 16)))
            await report(
                interaction,
                "Your role's color has been reset to invisible.",
                Status.SUCCESS,
            )
            return

        if action == "reassign":
            existing_role = find_role(get_color_role_name(member), guild)
            if not existing_role:
                await report(
                    interaction,
                    "Your color role does not exist, make a new one.",
                    Status.FAILURE,
                )
                return
            if existing_role in member.roles:
                await report(
                    interaction, "You already have your color role.", Status.FAILURE
                )
                return
            await member.add_roles(existing_role)
            await report(interaction, "Your role has been reassigned.", Status.SUCCESS)
            return

        # action is "set"
        if kind is None:
            await report(
                interaction, "Provide kind (hex/rgb/name/random/copy).", Status.FAILURE
            )
        else:
            await _handle_colorrole_set(
                interaction,
                member=member,
                guild=guild,
                kind=kind,
                hex6=hex6,
                r=r,
                g=g,
                b=b,
                name=name,
                role=role,
            )

    @app_commands.command(
        name="color", description="Color tools (info + interactive view)"
    )
    @app_commands.describe(
        kind="How to provide the color",
        hex6="Hex value (RRGGBB or #RRGGBB)",
        r="Red (0-255)",
        g="Green (0-255)",
        b="Blue (0-255)",
        name="CSS color name",
        role="Role to read color from",
    )
    async def color(
        self,
        interaction: discord.Interaction,
        kind: ColorKind,
        hex6: str | None = None,
        r: int | None = None,
        g: int | None = None,
        b: int | None = None,
        name: str | None = None,
        role: discord.Role | None = None,
    ) -> None:
        """Provide an embed with color info."""
        log_app_command(interaction)

        if kind == "hex":
            if not hex6 or not Color3.validate_hex(hex6):
                await report(interaction, "Provide a valid hex color.", Status.FAILURE)
                return
            color = Color3.from_hex6(hex6.lstrip("#").lower())

        elif kind == "rgb":
            if r is None or g is None or b is None or not Color3.validate_rgb(r, g, b):
                await report(
                    interaction, "Provide a valid RGB color (0-255).", Status.FAILURE
                )
                return
            color = Color3(r, g, b)

        elif kind == "name":
            if not name:
                await report(interaction, "Provide a CSS color name.", Status.FAILURE)
                return
            name = name.lower()
            if name not in CSS_COLOR_NAME_TO_HEX:
                await report(
                    interaction,
                    "Unknown color name. Use /colorlist for a list of supported names.",
                    Status.FAILURE,
                )
                return
            color = Color3.from_hex6(CSS_COLOR_NAME_TO_HEX[name])

        elif kind == "role":
            if role is None:
                await report(interaction, "Provide a role.", Status.FAILURE)
                return
            color = Color3(role.color.r, role.color.g, role.color.b)

        else:  # random
            color = Color3.random()

        embed, files = build_color_embed(
            title=f"#{color.as_hex6()} Info",
            description="Here's some information about your color.",
            color=color,
        )
        view = ColorView(
            interaction.user,
            color=color,
            in_server=(get_guild_interaction_data(interaction) is not None),
        )
        await view.send(interaction, embed=embed, files=files, ephemeral=False)

    @app_commands.command(
        name="colorlist",
        description="Get a list of all supported predefined color names",
    )
    @app_commands.describe(group="Group of colors to get the allowed names of")
    async def list(
        self,
        interaction: discord.Interaction,
        group: Literal[
            "red",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "pink",
            "brown",
            "white",
            "gray",
        ],
    ) -> None:
        """Provide a list of supported color names."""
        group_map = {
            "red": CSS_REDS,
            "orange": CSS_ORANGES,
            "yellow": CSS_YELLOWS,
            "green": CSS_GREENS,
            "blue": CSS_BLUES,
            "purple": CSS_PURPLES,
            "pink": CSS_PINKS,
            "brown": CSS_BROWNS,
            "white": CSS_WHITES,
            "gray": CSS_GRAYS,
        }

        log_app_command(interaction)

        colors = group_map[group]

        embed, icon = build_response_embed(
            title=f"{Visual.ART_PALETTE} {group.title()} Colors",
            description=f"Here's a list of supported {group} color names.",
            color=discord.Color(int(colors[group], 16)),
        )

        colors_str = ""
        for name, value in colors.items():
            colors_str += f"{name}  -  #{value}\n"

        embed.add_field(name=f"{group.title()} Colors", value=colors_str)

        await safe_send(interaction, embed=embed, file=icon, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(ColorCog(bot))
