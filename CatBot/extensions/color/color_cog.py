"""
Color tools and color role assignment commands.
"""

__author__ = "Gavin Borne"
__license__ = "MIT"


import logging
from io import BytesIO

# from typing import Literal, Union
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image

from ...role_tools import add_new_role_to_member, find_role, update_role_color
from ...ui.emoji import Status, report
from .color_tools import (
    # BLUES,
    # BROWNS,
    COLORS,
    # GRAYS,
    # GREENS,
    # ORANGES,
    # PINKS,
    # PURPLES,
    # REDS,
    # WHITES,
    # YELLOWS,
    hex2rgb,
    # invert_rgb,
    is_hex_value,
    is_rgb_value,
    random_rgb,
    # rgb2hex,
)


def create_color_role_name(member: discord.Member | discord.User, /) -> str:
    """Generate the color role name for the given member.

    Args:
        member (discord.Member | discord.User): The member to make the role for.

    Returns:
        str: The name of the new color role.
    """

    return f"{member.name}'s Color"


def generate_color_image(hex6: str, /) -> BytesIO:
    """Generate a color image based on the hex provided.

    Args:
        hex6 (str): The hex color.

    Returns:
        BytesIO: The color image as bytes.
    """

    rgb = hex2rgb(hex6)

    img = Image.new("RGB", (100, 100), (rgb[0], rgb[1], rgb[2]))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


def get_color_key(hex6: str, /) -> str | None:
    """Get the color key corresponding to a hex color.

    Args:
        hex6 (str): The hex color.

    Returns:
        str | None: The color key, if it exists, otherwise None.
    """

    if hex6 in COLORS.values():
        return [k for k, v in COLORS.items() if v == hex6][0]
    return None


async def handle_forbidden_exception(interaction: discord.Interaction, /) -> None:
    """Handle discord.Forbidden exceptions for color roles.

    Args:
        interaction (discord.Interaction): The interaction instance.
    """

    await report(
        interaction,
        "I do not have permissions to create roles. "
        + "Contact server administration about this please!",
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


class ColorCog(commands.Cog, name="Color Commands"):
    """Cog containing color commands."""

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""

        logging.info("ColorCog loaded")

    color_role_group = app_commands.Group(
        name="colorrole", description="color role commands"
    )

    @color_role_group.command(
        name="hex", description="Assign yourself a custom color role with hex"
    )
    @app_commands.describe(hex6="Hex value (#RRGGBB)")
    async def assign_hex(self, interaction: discord.Interaction, hex6: str) -> None:
        """Assign the user a new hex color role.
        This role is created if it does not exist, or if it does, it is updated.

        Args:
            interaction (discord.Interaction): The interaction instance.
            hex6 (str): The hex value (#RRGGBB).
        """

        logging.debug(
            "/colorrole hex hex6=%s invoked by %s", repr(hex6), interaction.user
        )

        guild = interaction.guild
        member = interaction.user
        if guild is None or isinstance(member, discord.User):
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        if not is_hex_value(hex6):
            await report(
                interaction,
                "Invalid hex value provided. Supported range: 000000-ffffff",
                Status.FAILURE,
            )
            return

        color = discord.Color(int(hex6.strip().strip("#"), 16))
        existing_role = find_role(create_color_role_name(member), guild)
        if existing_role:
            await update_role_color(existing_role, color)
            await report(
                interaction,
                f"Your role color has been updated to {hex6}.",
                Status.SUCCESS,
            )
            return

        try:
            await add_new_role_to_member(member, create_color_role_name(member), color)
            await report(
                interaction,
                f"You have been assigned a color role with the color {hex6}.",
                Status.SUCCESS,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @color_role_group.command(
        name="rgb", description="Assign yourself a custom color role with RGB"
    )
    @app_commands.describe(r="Red (0-255)", g="Green (0-255)", b="Blue (0-255)")
    async def assign_rgb(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ):
        """Assign the user a new RGB color.
        This role is created if it does not exist, or if it does, it is updated.

        Args:
            interaction (discord.Interaction): The interaction instance.
            r (int): The red value.
            g (int): The green value.
            b (int): The blue value.
        """

        logging.debug(
            "/colorrole rgb r=%s g=%s b=%s invoked by %s", r, g, b, interaction.user
        )

        guild = interaction.guild
        member = interaction.user
        if guild is None or isinstance(member, discord.User):
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        if not all(is_rgb_value(v) for v in (r, g, b)):
            await report(
                interaction,
                "Invalid RGB value provided. Supported range: 0-255",
                Status.FAILURE,
            )
            return

        color = discord.Color.from_rgb(r, g, b)
        existing_role = find_role(
            create_color_role_name(member),
            guild,
        )

        if existing_role:
            await update_role_color(existing_role, color)
            await report(
                interaction,
                f"Your role color has been updated to {(r, g, b)}.",
                Status.SUCCESS,
            )
            return

        try:
            await add_new_role_to_member(member, create_color_role_name(member), color)
            await report(
                interaction,
                f"You have been assigned a role with the color {(r, g, b)}.",
                Status.SUCCESS,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @color_role_group.command(
        name="name", description="Assign yourself a custom color with a color name"
    )
    @app_commands.describe(name="Color name (use /colorlist for a list of colors)")
    async def assign_color_name(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        """Assign the user a new color using a color name.
        This role is created if it does not exist, or if it does, it is updated.

        Args:
            interaction (discord.Interaction): The interaction instance.
            name (str): The name of the color.
        """

        logging.debug(
            "/colorrole name name=%s invoked by %s", repr(name), interaction.user
        )

        guild = interaction.guild
        member = interaction.user
        if guild is None or isinstance(member, discord.User):
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        name = name.lower()
        if name not in COLORS:
            await report(
                interaction,
                "Invalid color name provided. Use /color-list for a list of supported colors.",
                Status.FAILURE,
            )
            return

        color = discord.Color(int(COLORS[name], 16))
        existing_role = find_role(create_color_role_name(member), guild)

        if existing_role:
            await update_role_color(existing_role, color)
            await report(
                interaction,
                f"Your role color has been updated to {name}.",
                Status.SUCCESS,
            )
            return

        try:
            await add_new_role_to_member(member, create_color_role_name(member), color)
            await report(
                interaction,
                f"You have been assigned a role with the color {name}.",
                Status.SUCCESS,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @color_role_group.command(
        name="random", description="Assign yourself a random color"
    )
    @app_commands.describe(seed="Optional seed to use when generating the color")
    async def assign_random(
        self, interaction: discord.Interaction, seed: str | None = None
    ) -> None:
        """
        Assign the user a random color.
        This role is created if it does not exist, or if it does, it is updated.

        Args:
            interaction (discord.Interaction): The interaction instance.
            seed (str | None): The optional seed to use for the random generation.
        """

        logging.debug("/color role random invoked by %s", interaction.user)

        guild = interaction.guild
        member = interaction.user
        if guild is None or isinstance(member, discord.User):
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        r, g, b = random_rgb(seed=seed)
        color = discord.Color.from_rgb(r, g, b)
        existing_role = find_role(
            create_color_role_name(interaction.user),
            guild,
        )

        if existing_role:
            await update_role_color(existing_role, color)
            await report(
                interaction,
                f"Your role color has been updated to {(r, g, b)}.",
                Status.SUCCESS,
            )
            return

        try:
            await add_new_role_to_member(member, create_color_role_name(member), color)
            await report(
                interaction,
                f"You have been assigned a role with color {(r, g, b)}.",
                Status.SUCCESS,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)
