"""
color_roles.py
Color assignment cog for CatBot.
"""

# We disable this here to prevent warnings about using 'hex' as a variable name
# pylint: disable=redefined-builtin

import logging
from io import BytesIO
from typing import Literal, Union

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image

from ..CatBot_utils import emojis, generate_authored_embed_with_icon
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
    hex2rgb,
    invert_rgb,
    is_hex_value,
    is_rgb_value,
    random_rgb,
    rgb2hex,
)
from .role_manipulation import create_color_role, edit_color_role, find_existing_role


def create_role_name(user: Union[discord.Member, discord.User], /) -> str:
    """
    Generate the role name given `user`.
    Current format: "{user.name}'s Color"

    :param user: User to generate the role name for
    :type user: Union[Member, User]
    :return: `user`'s role name
    :rtype: str
    """

    # IF YOU CHANGE THE BELOW ROLE NAME FORMAT,
    # UPDATE THE DOCSTRING DAMNIT!!!!!!!!
    return f"{user.name}'s Color"


def generate_color_image(hex: str) -> BytesIO:
    """
    Generate a color image based on the value(s) provided.

    :param hex: Hex code
    :type hex: str
    :return: The color image
    :rtype: BytesIO
    """

    rgb = hex2rgb(hex)  # type: ignore

    # Create a 100x100 pixel image with the specified RGB color
    img = Image.new("RGB", (100, 100), (rgb[0], rgb[1], rgb[2]))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


def get_color_key(hex: str) -> Union[str, None]:
    """
    Get the color key corresponding to `hex`, if it exists.

    :param hex: Hex to check for the color name of
    :type hex: str
    :return: Color key if it was found, otherwise None
    :rtype: Union[str, None]
    """

    if hex in COLORS.values():
        return [k for k, v in COLORS.items() if v == hex][0]
    return None


async def handle_forbidden_exception(interaction: discord.Interaction, /) -> None:
    """
    Execute this function on discord.Forbidden exceptions.

    :param interaction: Interaction instance
    :type interaction: discord.Interaction
    """

    await interaction.response.send_message(
        f"{emojis.ERROR} I do not have permissions to create roles. "
        + "Contact server administration about this please!",
        ephemeral=True,
    )
    logging.warning("Failed to create role due to lack of permissions")


async def handle_http_exception(
    interaction: discord.Interaction, err: discord.HTTPException, /
) -> None:
    """
    Execute this function on discord.HTTPException exceptions.

    :param interaction: Interaction instance
    :type interaction: discord.Interaction
    :param err: Error that occurred
    :type err: discord.HTTPException
    """

    await interaction.response.send_message(
        f"{emojis.ERROR} An error occurred. Please try again.", ephemeral=True
    )
    logging.error("Failed to create role due to an unexpected error: %s", err)


class ColorCog(commands.Cog, name="Color Role Commands"):
    """
    Cog containing color role commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Run when the cog is ready to be used.
        """

        logging.info("ColorCog loaded")

    color_group = app_commands.Group(name="color", description="color commands")
    role_group = app_commands.Group(
        name="role",
        description="Assign yourself a custom color role",
        parent=color_group,
    )
    invert_group = app_commands.Group(
        name="invert", description="Invert a color", parent=color_group
    )
    info_group = app_commands.Group(
        name="info", description="Get information about a color", parent=color_group
    )

    @role_group.command(
        name="hex", description="Assign yourself a custom color role with hex"
    )
    @app_commands.describe(hex="Hex value (#RRGGBB)")
    async def assign_hex(
        self,
        interaction: discord.Interaction,
        hex: str,  # pylint: disable=redefined-builtin
    ) -> None:
        """
        Assign the user a new hex color.
        This role is created if it does not exist, or if it does, it is updated.
        """

        logging.info(
            "/color role hex hex=%s invoked by %s", repr(hex), interaction.user
        )

        if not is_hex_value(hex):
            await interaction.response.send_message(
                f"{emojis.X} Invalid hex value provided. Supported range: 000000-ffffff",
                ephemeral=True,
            )
            return

        color = discord.Color(int(hex.strip().strip("#"), 16))
        existing_role = find_existing_role(
            create_role_name(interaction.user),
            interaction.guild.roles,  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, hex)  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} Your role color has been updated to {hex}.",
                ephemeral=True,
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} You have been assigned a role with the color {hex}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_group.command(
        name="rgb", description="Assign yourself a custom color role with RGB"
    )
    @app_commands.describe(
        r="Red value (0-255)", g="Green value (0-255)", b="Blue value (0-255)"
    )
    async def assign_rgb(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ):
        """
        Assign the user a new RGB color.
        This role is created if it does not exist, or if it does, it is updated.
        """

        logging.info(
            "/color role rgb r=%s g=%s b=%s invoked by %s", r, g, b, interaction.user
        )

        if not all(is_rgb_value(v) for v in (r, g, b)):
            await interaction.response.send_message(
                f"{emojis.X} Invalid RGB value provided. Supported range: 0-255",
                ephemeral=True,
            )
            return

        color = discord.Color.from_rgb(r, g, b)
        existing_role = find_existing_role(
            create_role_name(interaction.user),
            interaction.guild.roles,  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, (r, g, b))  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} Your role color has been updated to {(r, g, b)}.",
                ephemeral=True,
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} You have been assigned a role with the color {(r, g, b)}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_group.command(
        name="name", description="Assign yourself a custom color with a color name"
    )
    @app_commands.describe(name="Color name (use /color-list for a list of colors)")
    async def assign_color_name(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        """
        Assign the user a new color using a color name.
        This role is created if it does not exist, or if it does, it is updated.
        """

        name = name.lower()

        logging.info(
            "/color role name name=%s invoked by %s", repr(name), interaction.user
        )

        if name not in COLORS:
            await interaction.response.send_message(
                f"{emojis.X} Invalid color name provided. "
                + "Use /color-list for a list of supported colors.",
                ephemeral=True,
            )
            return

        color = discord.Color(int(COLORS[name], 16))
        existing_role = find_existing_role(
            create_role_name(interaction.user),
            interaction.guild.roles,  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, color)  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} Your role color has been updated to {name}.",
                ephemeral=True,
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} You have been assigned a role with the color {name}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_group.command(name="random", description="Assign yourself a random color")
    @app_commands.describe(seed="Optional seed to use when generating the color")
    async def assign_random(
        self, interaction: discord.Interaction, seed: Union[str, None] = None
    ) -> None:
        """
        Assign the user a random color.
        This role is created if it does not exist, or if it does, it is updated.
        """

        logging.info("/color role random invoked by %s", interaction.user)

        r, g, b = random_rgb(seed=seed)
        color = discord.Color.from_rgb(r, g, b)
        existing_role = find_existing_role(
            create_role_name(interaction.user),
            interaction.guild.roles,  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, (r, g, b))  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} Your role color has been updated to {(r, g, b)}.",
                ephemeral=True,
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} You have been assigned a role with color {(r, g, b)}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_group.command(
        name="copy-color", description="Copy a role's color and assign it to yourself"
    )
    @app_commands.describe(role="Role to copy the color of")
    async def copy_role(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        """
        Copy `roles`'s color and assign it to the user as a color role.
        This role is created if it does not exist, or if it does, it is updated.
        """

        logging.info(
            "/color role copy-color role=%s invoked by %s", role, interaction.user
        )

        if role not in interaction.guild.roles:  # type: ignore
            await interaction.response.send_message(
                f"{emojis.X} The role was not found in this guild.", ephemeral=True
            )
            return

        color = role.color
        existing_role = find_existing_role(
            create_role_name(interaction.user),
            interaction.guild.roles,  # type: ignore
        )

        if existing_role:
            await edit_color_role(
                existing_role,
                color,
                interaction.user,
                (color.r, color.g, color.b),  # type: ignore
            )
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} Your role color has been updated to {(color.r, color.g, color.b)}.",
                ephemeral=True,
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"{emojis.CHECKMARK} You have been assigned a role with color {(color.r, color.g, color.b)}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_group.command(
        name="reset", description="Reset your color to the default (empty) color"
    )
    async def reset_color(self, interaction: discord.Interaction) -> None:
        """
        Reset the user's color.
        """

        logging.info("/color role reset invoked by %s", interaction.user)

        existing_role = find_existing_role(
            create_role_name(interaction.user),
            interaction.guild.roles,  # type: ignore
        )

        if not existing_role:
            await interaction.response.send_message(
                f"{emojis.X} You do not have a color role!", ephemeral=True
            )
            return

        await existing_role.edit(color=discord.Color(int("000000", 16)))
        await interaction.response.send_message(
            f"{emojis.CHECKMARK} Your role's color has been reset.", ephemeral=True
        )

    @role_group.command(
        name="reassign",
        description="Checks if you are missing your role and reassigns it if so",
    )
    async def reassign(self, interaction: discord.Interaction) -> None:
        """
        Check if the user is missing their role, and reassign it if so.
        """

        logging.info("/color role reassign invoked by %s", interaction.user)

        existing_role = find_existing_role(
            create_role_name(interaction.user),
            interaction.guild.roles,  # type: ignore
        )

        if not existing_role:
            await interaction.response.send_message(
                f"{emojis.X} Your color role does not exist, make a new one.",
                ephemeral=True,
            )
            return

        if existing_role in interaction.user.roles:  # type: ignore
            await interaction.response.send_message(
                f"{emojis.X} You already have your color role.", ephemeral=True
            )
            return

        await interaction.user.add_roles(existing_role)  # type: ignore
        await interaction.response.send_message(
            f"{emojis.CHECKMARK} Your role has been reassigned.", ephemeral=True
        )

    @color_group.command(
        name="color-list",
        description="Get a list of all supported predefined color names",
    )
    @app_commands.describe(group="Group of colors to get the allowed names of")
    async def color_list(
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
        """
        Provide a list of supported color names.
        """

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

        logging.info(
            "/color color-list group=%s invoked by %s", group, interaction.user
        )

        colors = group_map[group]

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} {group.title()} Colors",
            embed_description=f"Here's a list of supported {group} color names.",
            embed_color=discord.Color(int(colors[group], 16)),
        )

        colors_str = ""
        for name_, value in colors.items():
            colors_str += f"{name_.title()}  -  #{value}\n"

        embed.add_field(name=f"{group.title()} Colors", value=colors_str)

        await interaction.response.send_message(embed=embed, file=icon)

    @info_group.command(name="rgb", description="Get info about an RGB color")
    @app_commands.describe(
        r="Red value (0-255)", g="Green value (0-255)", b="Blue value (0-255)"
    )
    async def rgb_info(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ) -> None:
        """
        Get info about the RGB value.
        """

        logging.info(
            "/color info rgb r=%s g=%s b=%s invoked by %s", r, g, b, interaction.user
        )

        if not all(is_rgb_value(v) for v in (r, g, b)):
            await interaction.response.send_message(
                f"{emojis.X} Invalid RGB value provided. Supported range: 0-255",
                ephemeral=True,
            )
            return

        hex = rgb2hex(r, g, b)
        image = generate_color_image(hex)
        filename = f"{hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} {(r, g, b)} Info",
            embed_description="Here's some information about your color.",
            embed_color=discord.Color.from_rgb(r, g, b),
        )

        embed.add_field(name="Hex", value=f"#{hex}")

        key = get_color_key(hex)
        if key:
            embed.add_field(name="Color Name", value=key)

        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))

    @info_group.command(name="hex", description="Get info about a hex color")
    @app_commands.describe(hex="Hex value (#000000-#ffffff)")
    async def hex_info(self, interaction: discord.Interaction, hex: str) -> None:
        """
        Get info about the hex value.
        """

        logging.info(
            "/color info hex hex=%s invoked by %s", repr(hex), interaction.user
        )

        if not is_hex_value(hex):
            await interaction.response.send_message(
                f"{emojis.X} Invalid hex value provided. Supported range: 000000-ffffff",
                ephemeral=True,
            )
            return

        hex = hex.strip("#").lower()
        r, g, b = hex2rgb(hex)
        image = generate_color_image(hex)
        filename = f"{hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} #{hex} Info",
            embed_description="Here's some information about your color.",
            embed_color=discord.Color.from_rgb(r, g, b),
        )

        embed.add_field(name="RGB", value=f"{(r, g, b)}")

        key = get_color_key(hex)
        if key:
            embed.add_field(name="Color Name", value=key)

        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))

    @info_group.command(name="name", description="Get info about a color name")
    @app_commands.describe(
        name="Color name (use /color-list for a list of supported colors)"
    )
    async def name_info(self, interaction: discord.Interaction, name: str) -> None:
        """
        Get info about the hex value.
        """

        logging.info(
            "/color info name name=%s invoked by %s", repr(name), interaction.user
        )

        name = name.lower()

        if name not in COLORS:
            await interaction.response.send_message(
                f"{emojis.X} Invalid color name provided. "
                + "Use /color color-list for a list of supported colors",
                ephemeral=True,
            )
            return

        hex = COLORS[name]
        r, g, b = hex2rgb(hex)
        image = generate_color_image(hex)
        filename = f"{hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} {name.title()} Info",
            embed_description="Here's some information about your color.",
            embed_color=discord.Color.from_rgb(r, g, b),
        )

        embed.add_field(name="Hex", value=f"#{hex}")
        embed.add_field(name="RGB", value=f"{(r, g, b)}")
        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))

    @info_group.command(name="role", description="Get info about a role's color")
    @app_commands.describe(role="Role to get the color info of")
    async def role_info(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        """
        Get info about `role`'s color.
        """

        logging.info("/color info role role=%s invoked by %s", role, interaction.user)

        if role not in interaction.guild.roles:  # type: ignore
            await interaction.response.send_message(
                f"{emojis.X} The role was not found in this guild.", ephemeral=True
            )
            return

        r, g, b = role.color.r, role.color.g, role.color.b
        hex = rgb2hex(r, g, b)
        image = generate_color_image(hex)
        filename = f"{hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} {role.name} Color Info",
            embed_description="Here's some information about your role's color.",
            embed_color=role.color,
        )

        embed.add_field(name="Hex", value=f"#{hex}")
        embed.add_field(name="RGB", value=f"{(r, g, b)}")

        key = get_color_key(hex)
        if key:
            embed.add_field(name="Color Name", value=key)

        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))

    @color_group.command(name="random", description="Generate a random color.")
    @app_commands.describe(seed="Optional seed to use when generating the color")
    async def random_color(
        self, interaction: discord.Interaction, seed: Union[str, None] = None
    ) -> None:
        """
        Generate a random color.
        """

        logging.info("/color random invoked by %s", interaction.user)

        r, g, b = random_rgb(seed=seed)
        hex = rgb2hex(r, g, b)

        image = generate_color_image(hex)
        filename = f"{hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} Random Color",
            embed_description="Here's your randomly generated color.",
            embed_color=discord.Color.from_rgb(r, g, b),
        )

        embed.add_field(name="RGB", value=f"{(r, g, b)}")
        embed.add_field(name="Hex", value=f"#{hex}")

        key = get_color_key(hex)
        if key:
            embed.add_field(name="Color Name", value=key)

        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))

    @invert_group.command(name="rgb", description="Invert the RGB color")
    @app_commands.describe(
        r="Red value (0-255)", g="Green value (0-255)", b="Blue value (0-255)"
    )
    async def invert_rgb(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ) -> None:
        """
        Invert the RGB value.
        """

        logging.info(
            "/color invert rgb r=%s g=%s b=%s invoked by %s", r, g, b, interaction.user
        )

        if not all(is_rgb_value(v) for v in (r, g, b)):
            await interaction.response.send_message(
                f"{emojis.X} Invalid RGB value provided. Supported range: 0-255",
                ephemeral=True,
            )
            return

        nr, ng, nb = invert_rgb(r, g, b)
        hex = rgb2hex(nr, ng, nb)

        image = generate_color_image(hex)
        filename = f"{hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} Inverted color of ({r}, {g}, {b})",
            embed_description="Here's your inverted color.",
            embed_color=discord.Color.from_rgb(nr, ng, nb),
        )

        embed.add_field(name="RGB", value=f"{(nr, ng, nb)}")
        embed.add_field(name="Hex", value=f"#{hex}")

        key = get_color_key(hex)
        if key:
            embed.add_field(name="Color Name", value=key)

        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))

    @invert_group.command(name="hex", description="Invert the hex color")
    @app_commands.describe(hex="Hex color")
    async def invert_hex(self, interaction: discord.Interaction, hex: str) -> None:
        """
        Invert `hex`.
        """

        logging.info(
            "/color invert hex hex=%s invoked by %s", repr(hex), interaction.user
        )

        if not is_hex_value(hex):
            await interaction.response.send_message(
                f"{emojis.X} Invalid hex value provided. Supported range: 000000-ffffff",
                ephemeral=True,
            )
            return

        hex = hex.strip("#").lower()
        rgb = hex2rgb(hex)
        nr, ng, nb = invert_rgb(*rgb)
        new_hex = rgb2hex(nr, ng, nb)

        image = generate_color_image(new_hex)
        filename = f"{new_hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} Inverted color of #{hex}",
            embed_description="Here's your inverted color.",
            embed_color=discord.Color.from_rgb(nr, ng, nb),
        )

        embed.add_field(name="Hex", value=f"#{hex}")
        embed.add_field(name="RGB", value=f"{(nr, ng, nb)}")

        key = get_color_key(hex)
        if key:
            embed.add_field(name="Color Name", value=key)

        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))

    @invert_group.command(name="name", description="Invert the color name")
    @app_commands.describe(name="Color name (use /color-list for a list of colors)")
    async def invert_color_name(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        """
        Invert the color name.
        """

        logging.info(
            "/color invert name name=%s invoked by %s", repr(name), interaction.user
        )

        name = name.lower()

        if name not in COLORS:
            await interaction.response.send_message(
                f"{emojis.X} Invalid color name provided. Use /color-list for a list of supported colors",
                ephemeral=True,
            )
            return

        hex = COLORS[name]
        rgb = hex2rgb(hex)
        nr, ng, nb = invert_rgb(*rgb)
        new_hex = rgb2hex(nr, ng, nb)

        image = generate_color_image(new_hex)
        filename = f"{new_hex}.png"
        file = discord.File(fp=image, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.ART_PALETTE} Inverted color of #{hex}",
            embed_description="Here's your inverted color.",
            embed_color=discord.Color.from_rgb(nr, ng, nb),
        )

        embed.add_field(name="Hex", value=f"#{hex}")
        embed.add_field(name="RGB", value=f"{(nr, ng, nb)}")

        key = get_color_key(new_hex)
        if key:
            embed.add_field(name="Color Name", value=key)

        embed.set_image(url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, files=(file, icon))


async def setup(bot: commands.Bot):
    """
    Set up the ColorCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(ColorCog(bot))
