"""Color tools and color role assignment commands."""

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
    update_role_color,
)
from ...ui.emoji import Status, Visual
from .color_tools import (
    BLUES,
    BROWNS,
    COLORS,
    GRAYS,
    GREENS,
    ORANGES,
    PINKS,
    PURPLES,
    REDS,
    WHITES,
    YELLOWS,
    create_color_role_name,
    generate_color_image,
    get_color_key,
    hex2rgb,
    hex_is_valid,
    invert_rgb,
    random_rgb,
    rgb2hex,
    rgb_component_is_valid,
)

__author__ = "Gavin Borne"
__license__ = "MIT"


# TODO: make a generic UserUniqueView class that can only be
# interacted with by the original user
class ColorView(discord.ui.View):
    """View for interactive color actions (invert, revert, etc)."""

    def __init__(
        self,
        user: discord.abc.User,
        /,
        *,
        hex6: str,
        rgb: tuple[int, int, int],
        timeout: float | None = 60.0,
    ) -> None:
        """Create a new ColorView.

        Args:
            user (discord.User): The user that spawned the interaction.
            hex6 (str): The original hex color.
            rgb (tuple[int, int, int]): The original RGB color.
            timeout (float | None, optional): The timeout of the view. Defaults to 60.0.
        """
        super().__init__(timeout=timeout)
        self.user_id = user.id

        self.original_hex = hex6.strip("#").lower()  # sanitize hex
        self.original_r, self.original_g, self.original_b = rgb

        self.current_hex = self.original_hex
        self.current_r = self.original_r
        self.current_g = self.original_g
        self.current_b = self.original_b

    async def __check_user(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You can't interact with another user's embed!", ephemeral=True
            )
            return False
        return True

    async def __update_message(
        self, interaction: discord.Interaction, /, *, title: str, description: str
    ) -> None:
        embed, files = build_color_embed(
            title=title,
            description=description,
            hex6=self.current_hex,
            r=self.current_r,
            g=self.current_g,
            b=self.current_b,
        )

        await interaction.response.edit_message(
            embed=embed, attachments=files, view=self
        )

    @discord.ui.button(label="Invert", style=discord.ButtonStyle.primary)
    async def invert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Invert the color and update the embed.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        if not await self.__check_user(interaction):
            return

        nr, ng, nb = invert_rgb(self.current_r, self.current_g, self.current_b)
        new_hex = rgb2hex(nr, ng, nb)

        self.current_r, self.current_g, self.current_b = nr, ng, nb
        self.current_hex = new_hex

        await self.__update_message(
            interaction,
            title=f"Inverted color of #{self.original_hex}",
            description="Here's your inverted color.",
        )

    # TODO: darken, lighten, complement, assign as color role, etc buttons

    @discord.ui.button(label="Revert", style=discord.ButtonStyle.secondary)
    async def revert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Revert the current color to the original.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        if not await self.__check_user(interaction):
            return

        self.current_hex = self.original_hex
        self.current_r = self.original_r
        self.current_g = self.original_g
        self.current_b = self.original_b

        await self.__update_message(
            interaction,
            title=f"#{self.original_hex} Info",
            description="Here's some information about your color.",
        )


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
    *, title: str, description: str, hex6: str, r: int, g: int, b: int
) -> tuple[discord.Embed, list[discord.File]]:
    """Create the embeds and files needed to display color info.

    Args:
        title (str): _description_
        description (str): _description_
        hex6 (str): _description_
        r (int): _description_
        g (int): _description_
        b (int): _description_

    Returns:
        tuple[discord.Embed, list[discord.File]]: _description_
    """
    hex6 = hex6.strip("#").lower()  # normalize hex

    image = generate_color_image(hex6)
    filename = f"{hex6}.png"
    color_file = discord.File(fp=image, filename=filename)

    embed, icon = generate_response_embed(
        title=f"{Visual.ART_PALETTE} {title}",
        description=description,
        color=discord.Color.from_rgb(r, g, b),
    )

    embed.add_field(name="Hex", value=f"#{hex6}")
    embed.add_field(name="RGB", value=f"{(r, g, b)}")

    key = get_color_key(hex6)
    if key:
        embed.add_field(name="Color Name", value=key)

    embed.set_image(url=f"attachment://{filename}")

    return embed, [color_file, icon]


async def update_color_role(
    member: discord.Member,
    guild: discord.Guild,
    color: discord.Color,
    interaction: discord.Interaction,
) -> None:
    """Update the user's color role.

    Args:
        member (discord.Member): The member whose role to update.
        guild (discord.Guild): The guild to update the role in.
        color (discord.Color): The new role color.
        interaction (discord.Interaction): The interaction instance.
    """
    existing_role = find_role(create_color_role_name(member), guild)

    if existing_role:
        await update_role_color(existing_role, color)
        await report(
            interaction,
            f"Your role color has been updated to {color.to_rgb()}.",
            Status.SUCCESS,
        )
        return

    try:
        await add_new_role_to_member(member, create_color_role_name(member), color)
        await report(
            interaction,
            f"You have been assigned a role with the color {color.to_rgb()}.",
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
        name="color_role",
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

        if not hex_is_valid(hex6):
            await report(
                interaction,
                "Invalid hex value provided. Supported range: 000000-ffffff",
                Status.FAILURE,
            )
            return

        color = discord.Color(int(hex6.strip().strip("#"), 16))
        await update_color_role(interaction.user, interaction.guild, color, interaction)

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

        if not all(rgb_component_is_valid(c) for c in (r, g, b)):
            await report(
                interaction,
                "Invalid RGB component provided. Supported range: 0-255",
                Status.FAILURE,
            )
            return

        color = discord.Color.from_rgb(r, g, b)
        await update_color_role(interaction.user, interaction.guild, color, interaction)

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

        if name not in COLORS:
            await report(
                interaction,
                "Invalid color name provided. "
                "Use /color_list for a list of supported colors.",
                Status.FAILURE,
            )
            return

        color = discord.Color(int(COLORS[name], 16))
        await update_color_role(interaction.user, interaction.guild, color, interaction)

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

        r, g, b = random_rgb()
        color = discord.Color.from_rgb(r, g, b)
        await update_color_role(interaction.user, interaction.guild, color, interaction)

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
        await update_color_role(interaction.user, interaction.guild, color, interaction)

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
        await report(interaction, "Your role's color has been reset.", Status.SUCCESS)

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
            "red": REDS,
            "orange": ORANGES,
            "yellow": YELLOWS,
            "green": GREENS,
            "blue": BLUES,
            "purple": PURPLES,
            "pink": PINKS,
            "brown": BROWNS,
            "white": WHITES,
            "gray": GRAYS,
            "grey": GRAYS,
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

        await interaction.response.send_message(embed=embed, file=icon)

    @color_group.command(name="rgb", description="Get info about an RGB color")
    @app_commands.describe(
        r="Red value (0-255)", g="Green value (0-255)", b="Blue value (0-255)"
    )
    async def color_rgb(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ) -> None:
        """Get info about the RGB value."""
        log_app_command(interaction)

        if not all(rgb_component_is_valid(v) for v in (r, g, b)):
            await report(
                interaction,
                "Invalid RGB value provided. Supported range: 0-255",
                Status.FAILURE,
            )
            return

        hex6 = rgb2hex(r, g, b)

        embed, files = build_color_embed(
            title=f"{(r, g, b)} Info",
            description="Here's some information about your color.",
            hex6=hex6,
            r=r,
            g=g,
            b=b,
        )

        view = ColorView(interaction.user, hex6=hex6, rgb=(r, g, b))

        await interaction.response.send_message(embed=embed, files=files, view=view)

    @color_group.command(name="hex", description="Get info about a hex color")
    @app_commands.describe(hex6="Hex value (#000000-#ffffff)")
    async def color_hex(self, interaction: discord.Interaction, hex6: str) -> None:
        """Get info about the hex value."""
        log_app_command(interaction)

        if not hex_is_valid(hex6):
            await report(
                interaction,
                "Invalid hex value provided. Supported range: 000000-ffffff",
                Status.FAILURE,
            )
            return

        hex6 = hex6.strip("#").lower()
        r, g, b = hex2rgb(hex6)

        embed, files = build_color_embed(
            title=f"#{hex6} Info",
            description="Here's some information about your color.",
            hex6=hex6,
            r=r,
            g=g,
            b=b,
        )

        view = ColorView(interaction.user, hex6=hex6, rgb=(r, g, b))

        await interaction.response.send_message(embed=embed, files=files, view=view)

    @color_group.command(name="name", description="Get info about a color name")
    @app_commands.describe(name="Color name (use /list for a list of supported colors)")
    async def color_name(self, interaction: discord.Interaction, name: str) -> None:
        """Get info about the hex value."""
        log_app_command(interaction)

        name = name.lower()

        if name not in COLORS:
            await report(
                interaction,
                "Invalid color name provided. "
                "Use /color list for a list of supported colors!",
                Status.FAILURE,
            )
            return

        hex6 = COLORS[name]
        r, g, b = hex2rgb(hex6)

        embed, files = build_color_embed(
            title=f"#{hex6} Info",
            description="Here's some information about your color.",
            hex6=hex6,
            r=r,
            g=g,
            b=b,
        )

        view = ColorView(interaction.user, hex6=hex6, rgb=(r, g, b))

        await interaction.response.send_message(embed=embed, files=files, view=view)

    # TODO: maybe change this name to prevent confusion with color_role group
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

        r, g, b = role.color.r, role.color.g, role.color.b
        hex6 = rgb2hex(r, g, b)

        embed, files = build_color_embed(
            title=f"#{hex6} Info",
            description=f"Here's some information about {role.name}'s color.",
            hex6=hex6,
            r=r,
            g=g,
            b=b,
        )

        view = ColorView(interaction.user, hex6=hex6, rgb=(r, g, b))

        await interaction.response.send_message(embed=embed, files=files, view=view)

    @color_group.command(name="random", description="Generate a random color.")
    @app_commands.describe(seed="Optional seed to use when generating the color")
    async def color_random(self, interaction: discord.Interaction) -> None:
        """Generate a random color."""
        log_app_command(interaction)

        r, g, b = random_rgb()
        hex6 = rgb2hex(r, g, b)

        embed, files = build_color_embed(
            title=f"#{hex6} Info",
            description="Here's some information about your randomly generated color.",
            hex6=hex6,
            r=r,
            g=g,
            b=b,
        )

        view = ColorView(interaction.user, hex6=hex6, rgb=(r, g, b))

        await interaction.response.send_message(embed=embed, files=files, view=view)


async def setup(bot: commands.Bot) -> None:
    """Set up the ColorCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """
    await bot.add_cog(ColorCog(bot))
