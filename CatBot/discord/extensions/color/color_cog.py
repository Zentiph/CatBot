"""Color tools and color role assignment commands."""

# TODO implement more color info stuff for Color3 methods
# like relative luminance and hsl

from __future__ import annotations

import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from ....pawprints import cog_setup_log_msg, log_app_command
from ...interaction import (
    add_new_role_to_member,
    find_role,
    generate_response_embed,
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
    create_color_role_name,
    generate_color_image,
)

__author__ = "Gavin Borne"
__license__ = "MIT"


class LightenModal(RestrictedModal["ColorView"]):
    """Modal to ask the user how much to lighten the color."""

    amount: discord.ui.TextInput[LightenModal] = discord.ui.TextInput(
        label="Lighten amount (%)",
        placeholder="e.g. 20",
        min_length=1,
        max_length=3,
        required=True,
    )

    def __init__(self, view: ColorView) -> None:
        """Create a new color lighten modal.

        Args:
            view (ColorView): The view associated with the modal.
        """
        super().__init__(view, title="Lighten Color")

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        """Update the embed after the user submits a percentage.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
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

        embed, files = build_color_embed(
            title=f"Lightened {percentage:.0f}% from "
            f"#{self.view.original_color.as_hex6()}",
            description="Here's your lightened color.",
            color=lightened,
        )

        await safe_edit(interaction, embed=embed, attachments=files, view=self.view)


class DarkenModal(RestrictedModal["ColorView"]):
    """Modal to ask the user how much to darken the color."""

    amount: discord.ui.TextInput[DarkenModal] = discord.ui.TextInput(
        label="Darken amount (%)",
        placeholder="e.g. 20",
        min_length=1,
        max_length=3,
        required=True,
    )

    def __init__(self, view: ColorView) -> None:
        """Create a new color darken modal.

        Args:
            view (ColorView): The view associated with the modal.
        """
        super().__init__(view, title="Darken Color")

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        """Update the embed after the user submits a percentage.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
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

        embed, files = build_color_embed(
            title=f"Darkened {percentage:.0f}% from "
            f"#{self.view.original_color.as_hex6()}",
            description="Here's your darkened color.",
            color=darkened,
        )

        await interaction.response.edit_message(
            embed=embed, attachments=files, view=self.view
        )


class ColorView(RestrictedView):
    """View for interactive color actions (invert, revert, etc)."""

    def __init__(
        self,
        user: discord.abc.User,
        /,
        *,
        color: Color3,
        timeout: float | None = 60.0,
        in_server: bool,
    ) -> None:
        """Create a new ColorView.

        Args:
            user (discord.User): The user that spawned the interaction.
            color (Color3): The original color.
            timeout (float | None, optional): The timeout of the view. Defaults to 60.0.
            in_server (bool): Whether this view is being accessed in
                a server (True) or DM (False).
        """
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
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Invert the color and update the embed.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        inverted = self.current_color.invert()
        old_hex = self.current_color.as_hex6()
        self.current_color = inverted

        embed, files = build_color_embed(
            title=f"Inverted color of #{old_hex}",
            description="Here's your inverted color.",
            color=inverted,
        )
        await safe_edit(interaction, embed=embed, attachments=files, view=self)

    # TODO: complement, etc buttons

    @discord.ui.button(label="Lighten", style=discord.ButtonStyle.primary, row=1)
    async def lighten_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Lighten the color and update the embed.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        await interaction.response.send_modal(LightenModal(self))

    @discord.ui.button(label="Darken", style=discord.ButtonStyle.primary, row=1)
    async def darken_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Darken the color and update the embed.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        await interaction.response.send_modal(DarkenModal(self))

    @discord.ui.button(
        label="Set As Color Role",
        style=discord.ButtonStyle.primary,
        row=2,
        disabled=True,  # changed in __init__ if in a server
        custom_id="color:set_role",
    )
    async def set_as_role(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Set the current color as the user's color role.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        if interaction.guild is None or not isinstance(
            interaction.user, discord.Member
        ):
            await report(
                interaction, "This button only works in servers.", Status.FAILURE
            )
            return

        await update_color_role(
            interaction.user,
            interaction.guild,
            discord.Color.from_rgb(*self.current_color.as_rgb()),
            f"#{self.current_color.as_hex6()}",
            interaction,
        )

    @discord.ui.button(label="Revert", style=discord.ButtonStyle.secondary, row=2)
    async def revert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Revert the current color to the original.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        self.current_color = self.original_color

        embed, files = build_color_embed(
            title=f"#{self.original_color.as_hex6()} Info",
            description="Here's some information about your color.",
            color=self.original_color,
        )
        await safe_edit(interaction, embed=embed, attachments=files, view=self)


async def handle_forbidden_exception(interaction: discord.Interaction, /) -> None:
    """Handle discord.Forbidden exceptions for color roles.

    Args:
        interaction (discord.Interaction): The interaction instance.
    """
    await report(
        interaction,
        "I do not have permissions to create roles. "
        "Contact server administration about this please!",
        Status.ERROR,
    )
    logging.warning("Failed to create role due to lack of permissions")


async def handle_http_exception(
    interaction: discord.Interaction, err: discord.HTTPException, /
) -> None:
    """Handle unexpected discord.HTTPExceptions for color roles.

    Args:
        interaction (discord.Interaction): _description_
        err (discord.HTTPException): _description_
    """
    await report(interaction, "An error occurred. Please try again.", Status.ERROR)
    logging.error("Failed to create role due to an unexpected error: %s", err)


def build_color_embed(
    *, title: str, description: str, color: Color3
) -> tuple[discord.Embed, list[discord.File]]:
    """Create the embeds and files needed to display color info.

    Args:
        title (str): The title of the embed.
        description (str): The description of the embed.
        color (Color3): The color.

    Returns:
        tuple[discord.Embed, list[discord.File]]: The embed and required files.
    """
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

    name = Color3.get_color_name(hex6)
    if name:
        embed.add_field(name="Color Name", value=name)

    embed.set_image(url=f"attachment://{filename}")

    return embed, [color_file, icon]


async def update_color_role(
    member: discord.Member,
    guild: discord.Guild,
    color: discord.Color,
    color_repr: str,
    interaction: discord.Interaction,
) -> None:
    """Update the user's color role.

    Args:
        member (discord.Member): The member whose role to update.
        guild (discord.Guild): The guild to update the role in.
        color (discord.Color): The new role color.
        color_repr (str): A string representation of the new color.
        interaction (discord.Interaction): The interaction instance.
    """
    existing_role = find_role(create_color_role_name(member), guild)

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
        await add_new_role_to_member(member, create_color_role_name(member), color)
        await report(
            interaction,
            f"You have been assigned a role with the color {color_repr}.",
            Status.SUCCESS,
        )

    except discord.Forbidden:
        await handle_forbidden_exception(interaction)
    except discord.HTTPException as e:
        await handle_http_exception(interaction, e)


class ColorCog(commands.Cog, name="Color Role Commands"):
    """Cog containing color role commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create a new ColorCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    color_group = app_commands.Group(name="color", description="color commands")
    color_role_group = app_commands.Group(
        name="colorrole",
        description="Assign yourself a custom color role",
    )

    @color_role_group.command(
        name="hex", description="Assign yourself a custom color role with hex"
    )
    @app_commands.describe(hex6="Hex value (#RRGGBB)")
    async def color_role_hex(
        self,
        interaction: discord.Interaction,
        hex6: str,
    ) -> None:
        """Assign the user a new hex color.

        This role is created if it does not exist, or if it does, it is updated.
        """
        log_app_command(interaction)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        if not Color3.validate_hex(hex6):
            await report(
                interaction,
                "Invalid hex value provided. Supported range: 000000-ffffff",
                Status.FAILURE,
            )
            return

        color = discord.Color(int(hex6.strip().strip("#"), 16))
        await update_color_role(
            interaction.user, interaction.guild, color, hex6, interaction
        )

    @color_role_group.command(
        name="rgb", description="Assign yourself a custom color role with RGB"
    )
    @app_commands.describe(
        r="Red component (0-255)",
        g="Green component (0-255)",
        b="Blue component (0-255)",
    )
    async def color_role_rgb(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ) -> None:
        """Assign the user a new RGB color.

        This role is created if it does not exist, or if it does, it is updated.
        """
        log_app_command(interaction)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        if not Color3.validate_rgb(r, g, b):
            await report(
                interaction,
                "Invalid RGB component provided. Supported range: 0-255",
                Status.FAILURE,
            )
            return

        color = discord.Color.from_rgb(r, g, b)
        await update_color_role(
            interaction.user, interaction.guild, color, str((r, g, b)), interaction
        )

    @color_role_group.command(
        name="name", description="Assign yourself a custom color with a color name"
    )
    @app_commands.describe(name="Color name (use /color list for a list of colors)")
    async def color_role_name(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        """Assign the user a new color using a color name.

        This role is created if it does not exist, or if it does, it is updated.
        """
        log_app_command(interaction)

        name = name.lower()

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        if name not in CSS_COLOR_NAME_TO_HEX:
            await report(
                interaction,
                "Invalid color name provided. "
                "Use /color list for a list of supported colors.",
                Status.FAILURE,
            )
            return

        color = discord.Color(int(CSS_COLOR_NAME_TO_HEX[name], 16))
        await update_color_role(
            interaction.user, interaction.guild, color, name, interaction
        )

    @color_role_group.command(
        name="random", description="Assign yourself a random color"
    )
    async def color_role_random(self, interaction: discord.Interaction) -> None:
        """Assign the user a random color.

        This role is created if it does not exist, or if it does, it is updated.
        """
        log_app_command(interaction)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        color = Color3.random().as_discord_color()
        await update_color_role(
            interaction.user,
            interaction.guild,
            color,
            f"{color.to_rgb()!s} (random)",
            interaction,
        )

    @color_role_group.command(
        name="copy", description="Copy a role's color and assign it to yourself"
    )
    @app_commands.describe(role="Role to copy the color of")
    async def color_role_copy(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        """Copy `roles`'s color and assign it to the user as a color role.

        This role is created if it does not exist, or if it does, it is updated.
        """
        log_app_command(interaction)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        if role not in interaction.guild.roles:
            await report(
                interaction, "The role was not found in this guild.", Status.FAILURE
            )
            return

        color = role.color
        await update_color_role(
            interaction.user,
            interaction.guild,
            color,
            f"{color.to_rgb()!s} (copied from {role.name})",
            interaction,
        )

    @color_role_group.command(
        name="reset", description="Reset your color to the default (empty) color"
    )
    async def color_role_reset(self, interaction: discord.Interaction) -> None:
        """Reset the user's color."""
        log_app_command(interaction)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        existing_role = find_role(
            create_color_role_name(interaction.user),
            interaction.guild,
        )

        if not existing_role:
            await report(interaction, "You do not have a color role!", Status.FAILURE)
            return

        await existing_role.edit(color=discord.Color(int("000000", 16)))
        await report(
            interaction,
            "Your role's color has been reset to invisible.",
            Status.SUCCESS,
        )

    @color_role_group.command(
        name="reassign",
        description="Checks if you are missing your role and reassigns it if so",
    )
    async def color_role_reassign(self, interaction: discord.Interaction) -> None:
        """Check if the user is missing their role, and reassign it if so."""
        log_app_command(interaction)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        existing_role = find_role(
            create_color_role_name(interaction.user),
            interaction.guild,
        )

        if not existing_role:
            await report(
                interaction,
                "Your color role does not exist, make a new one.",
                Status.FAILURE,
            )
            return

        if existing_role in interaction.user.roles:
            await report(
                interaction, "You already have your color role.", Status.FAILURE
            )
            return

        await interaction.user.add_roles(existing_role)
        await report(interaction, "Your role has been reassigned.", Status.SUCCESS)

    @color_group.command(
        name="list",
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
            "grey",
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
            "grey": CSS_GRAYS,
        }

        log_app_command(interaction)

        colors = group_map[group]

        embed, icon = generate_response_embed(
            title=f"{Visual.ART_PALETTE} {group.title()} Colors",
            description=f"Here's a list of supported {group} color names.",
            color=discord.Color(int(colors[group], 16)),
        )

        colors_str = ""
        for name_, value in colors.items():
            colors_str += f"{name_.title()}  -  #{value}\n"

        embed.add_field(name=f"{group.title()} Colors", value=colors_str)

        await safe_send(interaction, embed=embed, file=icon, ephemeral=False)

    @color_group.command(name="rgb", description="Get info about an RGB color")
    @app_commands.describe(
        r="Red value (0-255)", g="Green value (0-255)", b="Blue value (0-255)"
    )
    async def color_rgb(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ) -> None:
        """Get info about the RGB value."""
        log_app_command(interaction)

        if not Color3.validate_rgb(r, g, b):
            await report(
                interaction,
                "Invalid RGB value provided. Supported range: 0-255",
                Status.FAILURE,
            )
            return

        color = Color3(r, g, b)

        embed, files = build_color_embed(
            title=f"{(r, g, b)} Info",
            description="Here's some information about your color.",
            color=color,
        )

        view = ColorView(
            interaction.user,
            color=color,
            in_server=(interaction.guild is not None),
        )
        await view.send(interaction, embed=embed, files=files, ephemeral=False)

    @color_group.command(name="hex", description="Get info about a hex color")
    @app_commands.describe(hex6="Hex value (#000000-#ffffff)")
    async def color_hex(self, interaction: discord.Interaction, hex6: str) -> None:
        """Get info about the hex value."""
        log_app_command(interaction)

        if not Color3.validate_hex(hex6):
            await report(
                interaction,
                "Invalid hex value provided. Supported range: 000000-ffffff",
                Status.FAILURE,
            )
            return

        hex6 = hex6.strip("#").lower()
        color = Color3.from_hex6(hex6)

        embed, files = build_color_embed(
            title=f"#{hex6} Info",
            description="Here's some information about your color.",
            color=color,
        )

        view = ColorView(
            interaction.user,
            color=color,
            in_server=(interaction.guild is not None),
        )
        await view.send(interaction, embed=embed, files=files, ephemeral=False)

    @color_group.command(name="name", description="Get info about a color name")
    @app_commands.describe(
        name="Color name (use /color list for a list of supported colors)"
    )
    async def color_name(self, interaction: discord.Interaction, name: str) -> None:
        """Get info about the hex value."""
        log_app_command(interaction)

        name = name.lower()

        if name not in CSS_COLOR_NAME_TO_HEX:
            await report(
                interaction,
                "Invalid color name provided. "
                "Use /color list for a list of supported colors!",
                Status.FAILURE,
            )
            return

        hex6 = CSS_COLOR_NAME_TO_HEX[name]
        color = Color3.from_hex6(hex6)

        embed, files = build_color_embed(
            title=f"#{hex6} Info",
            description="Here's some information about your color.",
            color=color,
        )

        view = ColorView(
            interaction.user,
            color=color,
            in_server=(interaction.guild is not None),
        )
        await view.send(interaction, embed=embed, files=files, ephemeral=False)

    @color_group.command(name="role", description="Get info about a role's color")
    @app_commands.describe(role="Role to get the color info of")
    async def color_role(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        """Get info about `role`'s color."""
        log_app_command(interaction)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        if role not in interaction.guild.roles:
            await report(
                interaction, "The role was not found in this guild.", Status.FAILURE
            )
            return

        color = Color3(role.color.r, role.color.g, role.color.b)

        embed, files = build_color_embed(
            title=f"#{color.as_hex6()} Info",
            description=f"Here's some information about {role.name}'s color.",
            color=color,
        )

        view = ColorView(
            interaction.user,
            color=color,
            in_server=True,
        )
        await view.send(interaction, embed=embed, files=files, ephemeral=False)

    @color_group.command(name="random", description="Generate a random color.")
    async def color_random(self, interaction: discord.Interaction) -> None:
        """Generate a random color."""
        log_app_command(interaction)

        color = Color3.random()

        embed, files = build_color_embed(
            title=f"#{color.as_hex6()} Info",
            description="Here's some information about your randomly generated color.",
            color=color,
        )

        view = ColorView(
            interaction.user,
            color=color,
            in_server=(interaction.guild is not None),
        )
        await view.send(interaction, embed=embed, files=files, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(ColorCog(bot))
