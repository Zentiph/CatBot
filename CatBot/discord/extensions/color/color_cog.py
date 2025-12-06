"""Color tools and color role assignment commands."""

__author__ = "Gavin Borne"
__license__ = "MIT"


import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from ....pawprints import cog_setup_log_msg
from ...interaction import add_new_role_to_member, find_role, report, update_role_color
from ...ui.emoji import Status
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
    hex_is_valid,
    random_rgb,
    rgb_component_is_valid,
)

# TODO make some kind of general func call logger that will grab the command
# name and param automatically and fill it out


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
    invert_group = app_commands.Group(
        name="invert", description="Invert a color", parent=color_group
    )
    info_group = app_commands.Group(
        name="info", description="Get information about a color", parent=color_group
    )

    @color_role_group.command(
        name="hex", description="Assign yourself a custom color role with hex"
    )
    @app_commands.describe(hex6="Hex value (#RRGGBB)")
    async def assign_hex(
        self,
        interaction: discord.Interaction,
        hex6: str,
    ) -> None:
        """Assign the user a new hex color.

        This role is created if it does not exist, or if it does, it is updated.
        """
        logging.debug("/color_role hex hex6=%r invoked by %s", hex6, interaction.user)

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
        existing_role = find_role(
            create_color_role_name(interaction.user),
            interaction.guild,
        )

        if existing_role is not None:
            await update_role_color(existing_role, color)
            await report(
                interaction,
                f"Your role color has been updated to {hex6}.",
                Status.SUCCESS,
            )
            return

        try:
            await add_new_role_to_member(
                interaction.user, create_color_role_name(interaction.user), color
            )
            await report(
                interaction,
                f"You have been assigned a role with the color {hex6}.",
                Status.SUCCESS,
            )

        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @color_role_group.command(
        name="rgb", description="Assign yourself a custom color role with RGB"
    )
    @app_commands.describe(
        r="Red component (0-255)",
        g="Green component (0-255)",
        b="Blue component (0-255)",
    )
    async def assign_rgb(
        self, interaction: discord.Interaction, r: int, g: int, b: int
    ) -> None:
        """Assign the user a new RGB color.

        This role is created if it does not exist, or if it does, it is updated.
        """
        logging.debug(
            "/color_role rgb r=%s g=%s b=%s invoked by %s", r, g, b, interaction.user
        )

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
        existing_role = find_role(
            create_color_role_name(interaction.user),
            interaction.guild,
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
            await add_new_role_to_member(
                interaction.user, create_color_role_name(interaction.user), color
            )
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
    @app_commands.describe(name="Color name (use /color list for a list of colors)")
    async def assign_color_name(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        """Assign the user a new color using a color name.

        This role is created if it does not exist, or if it does, it is updated.
        """
        name = name.lower()

        logging.debug("/color_role name name=%r invoked by %s", name, interaction.user)

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
        existing_role = find_role(
            create_color_role_name(interaction.user),
            interaction.guild,
        )

        if existing_role:
            await update_role_color(existing_role, color)
            await report(
                interaction,
                f"Your role color has been updated to {name}.",
                Status.SUCCESS,
            )
            return

        try:
            await add_new_role_to_member(
                interaction.user, create_color_role_name(interaction.user), color
            )
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
    async def assign_random(self, interaction: discord.Interaction) -> None:
        """Assign the user a random color.

        This role is created if it does not exist, or if it does, it is updated.
        """
        logging.debug("/color_role random invoked by %s", interaction.user)

        if isinstance(interaction.user, discord.User) or interaction.guild is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        r, g, b = random_rgb()
        color = discord.Color.from_rgb(r, g, b)
        existing_role = find_role(
            create_color_role_name(interaction.user),
            interaction.guild,
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
            await add_new_role_to_member(
                interaction.user, create_color_role_name(interaction.user), color
            )
            await report(
                interaction,
                f"You have been assigned a role with color {(r, g, b)}.",
                Status.SUCCESS,
            )

        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @color_role_group.command(
        name="copy_color", description="Copy a role's color and assign it to yourself"
    )
    @app_commands.describe(role="Role to copy the color of")
    async def copy_role(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        """Copy `roles`'s color and assign it to the user as a color role.

        This role is created if it does not exist, or if it does, it is updated.
        """
        logging.debug(
            "/color_role copy_color role=%s invoked by %s", role, interaction.user
        )

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
        existing_role = find_role(
            create_color_role_name(interaction.user),
            interaction.guild,
        )

        if existing_role:
            await update_role_color(
                existing_role,
                color,
            )
            await report(
                interaction,
                f"Your role color has been updated to {(color.r, color.g, color.b)}.",
                Status.SUCCESS,
            )
            return

        try:
            await add_new_role_to_member(
                interaction.user, create_color_role_name(interaction.user), color
            )
            await report(
                interaction,
                "You have been assigned a role with color "
                f"{(color.r, color.g, color.b)}.",
                Status.SUCCESS,
            )

        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @color_role_group.command(
        name="reset", description="Reset your color to the default (empty) color"
    )
    async def reset_color(self, interaction: discord.Interaction) -> None:
        """Reset the user's color."""
        logging.debug("/color_role reset invoked by %s", interaction.user)

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
    async def reassign(self, interaction: discord.Interaction) -> None:
        """Check if the user is missing their role, and reassign it if so."""
        logging.debug("/color_role reassign invoked by %s", interaction.user)

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

        logging.info("/color list group=%s invoked by %s", group, interaction.user)

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
        """Get info about the RGB value."""
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
        """Get info about the hex value."""
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
        """Get info about the hex value."""
        logging.info(
            "/color info name name=%s invoked by %s", repr(name), interaction.user
        )

        name = name.lower()

        if name not in COLORS:
            await interaction.response.send_message(
                f"{emojis.X} Invalid color name provided. "
                "Use /color color-list for a list of supported colors",
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
        """Get info about `role`'s color."""
        logging.info("/color info role role=%s invoked by %s", role, interaction.user)

        if role not in interaction.guild.roles:
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
        """Generate a random color."""
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
        """Invert the RGB value."""
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
        """Invert `hex`."""
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
        """Invert the color name."""
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
    """Set up the ColorCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """
    await bot.add_cog(ColorCog(bot))
