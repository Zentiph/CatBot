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
    add_new_role_to_member,
    find_role,
    generate_response_embed,
    get_guild_interaction_data,
    report,
    safe_edit,
    safe_send,
    update_role_color,
)
from ...ui.emoji import Status, Visual
from ...views import RestrictedModal, RestrictedView
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
    generate_color_image,
)

__author__ = "Gavin Borne"
__license__ = "MIT"


ColorRoleAction = Literal["set", "reset", "reassign"]
ColorRoleKind = Literal["hex", "rgb", "name", "random", "copy"]
ColorKind = Literal["hex", "rgb", "name", "role", "random"]


def _create_color_role_name(member: discord.Member, /) -> str:
    return f"{member.id}'s Color Role"


def _build_color_embed(
    *, title: str, description: str, color: Color3
) -> tuple[discord.Embed, list[discord.File]]:
    hex6 = color.as_hex6()

    image = generate_color_image(color)
    filename = f"{hex6}.png"
    color_file = discord.File(fp=image, filename=filename)

    embed, icon = generate_response_embed(
        title=f"{Visual.ART_PALETTE} {title}",
        description=description,
        color=color.as_discord_color(),
    )

    embed.add_field(name="Hex", value=f"#{hex6}")
    embed.add_field(name="RGB", value=f"{color.as_rgb()}")
    hsl = color.as_hsl()
    embed.add_field(
        name="HSL",
        value=f"({hsl[0]:.0f}, {(hsl[1] * 100):.0f}%, {(hsl[2] * 100):.0f}%)",
    )

    name = Color3.get_color_name(hex6)
    if name:
        embed.add_field(name="Color Name", value=name)

    embed.set_image(url=f"attachment://{filename}")

    return embed, [color_file, icon]


async def _update_color_role(
    member: discord.Member,
    guild: discord.Guild,
    color: discord.Color,
    color_repr: str,
    interaction: discord.Interaction,
) -> None:
    existing_role = find_role(_create_color_role_name(member), guild)

    if existing_role:
        if existing_role.color == color:
            await report(
                interaction, "This is already your role color!", Status.FAILURE
            )
            return

        await update_role_color(existing_role, color)
        await report(
            interaction,
            f"Your role color has been updated to {color_repr}.",
            Status.SUCCESS,
        )
        return

    try:
        await add_new_role_to_member(member, _create_color_role_name(member), color)
        await report(
            interaction,
            f"You have been assigned a role with the color {color_repr}.",
            Status.SUCCESS,
        )

    except discord.Forbidden:
        await report(
            interaction,
            "I do not have permissions to create roles. "
            "Contact server administration about this please!",
            Status.ERROR,
        )
        logging.warning("Failed to create role due to lack of permissions")
    except discord.HTTPException:
        await report(interaction, "An error occurred. Please try again.", Status.ERROR)
        logging.exception("Failed to create role due to an unexpected error: %s")


class _LightenModal(RestrictedModal["_ColorView"]):
    amount: discord.ui.TextInput[_LightenModal] = discord.ui.TextInput(
        label="Lighten amount (%)",
        placeholder="e.g. 20",
        min_length=1,
        max_length=3,
        required=True,
    )

    def __init__(self, view: _ColorView) -> None:
        super().__init__(view, title="Lighten Color")

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        try:
            percentage = float(str(self.amount))
        except ValueError:
            await report(
                interaction, "Please enter a valid percentage.", Status.FAILURE
            )
            return

        percent_max = 100
        if percentage < 0 or percentage > percent_max:
            await report(
                interaction,
                "The percentage entered must be between 0% and 100%.",
                Status.FAILURE,
            )
            return

        lightened = self.view.current_color.lighten(percentage)
        self.view.current_color = lightened

        embed, files = _build_color_embed(
            title=f"Lightened {percentage:.0f}% from "
            f"#{self.view.original_color.as_hex6()}",
            description="Here's your lightened color.",
            color=lightened,
        )

        await safe_edit(interaction, embed=embed, attachments=files, view=self.view)


class _DarkenModal(RestrictedModal["_ColorView"]):
    amount: discord.ui.TextInput[_DarkenModal] = discord.ui.TextInput(
        label="Darken amount (%)",
        placeholder="e.g. 20",
        min_length=1,
        max_length=3,
        required=True,
    )

    def __init__(self, view: _ColorView) -> None:
        super().__init__(view, title="Darken Color")

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        try:
            percentage = float(str(self.amount))
        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid percentage.", ephemeral=True
            )
            return

        percent_max = 100
        if percentage < 0 or percentage > percent_max:
            await report(
                interaction,
                "The percentage entered must be between 0% and 100%.",
                Status.FAILURE,
            )
            return

        darkened = self.view.current_color.darken(percentage)
        self.view.current_color = darkened

        embed, files = _build_color_embed(
            title=f"Darkened {percentage:.0f}% from "
            f"#{self.view.original_color.as_hex6()}",
            description="Here's your darkened color.",
            color=darkened,
        )

        await interaction.response.edit_message(
            embed=embed, attachments=files, view=self.view
        )


class _ColorView(RestrictedView):
    def __init__(
        self,
        user: discord.abc.User,
        /,
        *,
        color: Color3,
        timeout: float | None = 60.0,
        in_server: bool,
    ) -> None:
        super().__init__(user=user, timeout=timeout)

        self.original_color = color
        self.current_color = self.original_color

        if in_server:
            item = discord.utils.get(self.children, custom_id="color:set_role")
            if isinstance(item, discord.ui.Button):
                # enable "Set As Color Role" button in servers
                item.disabled = False

    @discord.ui.button(label="Invert", style=discord.ButtonStyle.primary, row=0)
    async def invert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[_ColorView]
    ) -> None:
        inverted = self.current_color.invert()
        old_hex = self.current_color.as_hex6()
        self.current_color = inverted

        embed, files = _build_color_embed(
            title=f"Inverted color of #{old_hex}",
            description="Here's your inverted color.",
            color=inverted,
        )
        await safe_edit(interaction, embed=embed, attachments=files, view=self)

    @discord.ui.button(label="Lighten", style=discord.ButtonStyle.primary, row=1)
    async def lighten_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[_ColorView]
    ) -> None:
        await interaction.response.send_modal(_LightenModal(self))

    @discord.ui.button(label="Darken", style=discord.ButtonStyle.primary, row=1)
    async def darken_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[_ColorView]
    ) -> None:
        await interaction.response.send_modal(_DarkenModal(self))

    @discord.ui.button(
        label="Set As Color Role",
        style=discord.ButtonStyle.primary,
        row=2,
        disabled=True,  # changed in __init__ if in a server
        custom_id="color:set_role",
    )
    async def set_as_role(
        self, interaction: discord.Interaction, _button: discord.ui.Button[_ColorView]
    ) -> None:
        if interaction.guild is None or not isinstance(
            interaction.user, discord.Member
        ):
            await report(
                interaction, "This button only works in servers.", Status.FAILURE
            )
            return

        await _update_color_role(
            interaction.user,
            interaction.guild,
            discord.Color.from_rgb(*self.current_color.as_rgb()),
            f"#{self.current_color.as_hex6()}",
            interaction,
        )

    @discord.ui.button(label="Revert", style=discord.ButtonStyle.secondary, row=2)
    async def revert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[_ColorView]
    ) -> None:
        self.current_color = self.original_color

        embed, files = _build_color_embed(
            title=f"#{self.original_color.as_hex6()} Info",
            description="Here's some information about your color.",
            color=self.original_color,
        )
        await safe_edit(interaction, embed=embed, attachments=files, view=self)


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
            existing_role = find_role(_create_color_role_name(member), guild)
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
            existing_role = find_role(_create_color_role_name(member), guild)
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
            return

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

        await _update_color_role(member, guild, discord_color, color_repr, interaction)

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

        embed, files = _build_color_embed(
            title=f"#{color.as_hex6()} Info",
            description="Here's some information about your color.",
            color=color,
        )
        view = _ColorView(
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

        embed, icon = generate_response_embed(
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
