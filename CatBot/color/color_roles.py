"""
color_roles.py
Color assignment cog for CatBot.
"""

import logging
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands

from .colors import COLORS, is_hex_value, is_rgb_value, random_rgb
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


async def handle_forbidden_exception(interaction: discord.Interaction, /) -> None:
    """
    Execute this function on discord.Forbidden exceptions.

    :param interaction: Interaction instance
    :type interaction: discord.Interaction
    """

    await interaction.response.send_message(
        "I do not have permissions to create roles. "
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
        "An error occurred. Please try again.", ephemeral=True
    )
    logging.error("Failed to create role due to an unexpected error: %s", err)


class ColorRoleCog(commands.Cog, name="Color Role Commands"):
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

        logging.info("ColorRoleCog loaded")

    role_assign_group = app_commands.Group(
        name="color-role", description="Assign yourself a custom color role"
    )

    @role_assign_group.command(
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

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param hex: Hex value
        :type hex: str
        """

        logging.info("/color-role hex hex=%s invoked by %s", hex, interaction.user)

        if not is_hex_value(hex):
            await interaction.response.send_message(
                "Invalid hex value provided. Supported range: 000000-ffffff",
                ephemeral=True,
            )
            logging.info("/color-role hex halted due to invalid value")
            return

        color = discord.Color(int(hex.strip().strip("#"), 16))
        existing_role = find_existing_role(
            create_role_name(interaction.user), interaction.guild.roles  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, hex)  # type: ignore
            await interaction.response.send_message(
                f"Your role color has been updated to {hex}.", ephemeral=True
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"You have been assigned a role with the color {hex}.", ephemeral=True
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_assign_group.command(
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

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param r: R value
        :type r: int
        :param g: G value
        :type g: int
        :param b: B value
        :type b: int
        """

        logging.info(
            "/color-role rgb r=%s g=%s b=%s invoked by %s", r, g, b, interaction.user
        )

        if not all(is_rgb_value(v) for v in (r, g, b)):
            await interaction.response.send_message(
                "Invalid RGB value provided. Supported range: 0-255", ephemeral=True
            )
            logging.info("/color-role rgb halted due to invalid value")
            return

        color = discord.Color.from_rgb(r, g, b)
        existing_role = find_existing_role(
            create_role_name(interaction.user), interaction.guild.roles  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, (r, g, b))  # type: ignore
            await interaction.response.send_message(
                f"Your role color has been updated to {(r, g, b)}.", ephemeral=True
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"You have been assigned a role with the color {(r, g, b)}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_assign_group.command(
        name="name", description="Assign yourself a custom color with a color name"
    )
    @app_commands.describe(name="Color name (use /colors for a list of colors)")
    async def assign_color_name(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        """
        Assign the user a new color using a color name.
        This role is created if it does not exist, or if it does, it is updated.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param name: Color name
        :type name: str
        """

        name = name.lower()

        logging.info("/color-role name name=%s invoked by %s", name, interaction.user)

        if name not in COLORS:
            await interaction.response.send_message(
                "Invalid color name provided. Use /colors for a list of supported colors.",
                ephemeral=True,
            )
            logging.info("/color-role name halted due to invalid value")
            return

        color = discord.Color(int(COLORS[name], 16))
        existing_role = find_existing_role(
            create_role_name(interaction.user), interaction.guild.roles  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, color)  # type: ignore
            await interaction.response.send_message(
                f"Your role color has been updated to {name}.", ephemeral=True
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"You have been assigned a role with the color {name}.", ephemeral=True
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_assign_group.command(
        name="random", description="Assign yourself a random color"
    )
    @app_commands.describe(seed="Optional seed to use when generating the color")
    async def assign_random(
        self, interaction: discord.Interaction, seed: Union[str, None] = None
    ) -> None:
        """
        Assign the user a random color.
        This role is created if it does not exist, or if it does, it is updated.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param seed: Optional seed, defaults to None
        :type seed: str | None, optional
        """

        logging.info("/color-role random invoked by %s", interaction.user)

        r, g, b = random_rgb(seed=seed)
        color = discord.Color.from_rgb(r, g, b)
        existing_role = find_existing_role(
            create_role_name(interaction.user), interaction.guild.roles  # type: ignore
        )

        if existing_role:
            await edit_color_role(existing_role, color, interaction.user, (r, g, b))  # type: ignore
            await interaction.response.send_message(
                f"Your role color has been updated to {(r, g, b)}.", ephemeral=True
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"You have been assigned a role with color {(r, g, b)}.", ephemeral=True
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_assign_group.command(
        name="copy-color", description="Copy a role's color and assign it to yourself"
    )
    @app_commands.describe(role="Role to copy the color of")
    async def copy_role(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        """
        Copy `roles`'s color and assign it to the user as a color role.
        This role is created if it does not exist, or if it does, it is updated.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param role: Role to copy the color of
        :type role: discord.Role
        """

        logging.info(
            "/color-role copy-color role=%s invoked by %s", role, interaction.user
        )

        if role not in interaction.guild.roles:  # type: ignore
            await interaction.response.send_message(
                "Role was not found in this guild.", ephemeral=True
            )
            logging.info("/color-role copy-color halted due to invalid role")
            return

        color = role.color
        existing_role = find_existing_role(
            create_role_name(interaction.user), interaction.guild.roles  # type: ignore
        )

        if existing_role:
            await edit_color_role(
                existing_role, color, interaction.user, (color.r, color.g, color.b)  # type: ignore
            )
            await interaction.response.send_message(
                f"Your role color has been updated to {(color.r, color.g, color.b)}.",
                ephemeral=True,
            )
            return

        try:
            await create_color_role(interaction.user, color, interaction.guild)  # type: ignore
            await interaction.response.send_message(
                f"You have been assigned a role with color {(color.r, color.g, color.b)}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await handle_forbidden_exception(interaction)
        except discord.HTTPException as e:
            await handle_http_exception(interaction, e)

    @role_assign_group.command(
        name="reset", description="Reset your color to the default (empty) color"
    )
    async def reset_color(self, interaction: discord.Interaction) -> None:
        """
        Reset the user's color.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        """

        logging.info("/color-role reset invoked by %s", interaction.user)

        existing_role = find_existing_role(
            create_role_name(interaction.user), interaction.guild.roles  # type: ignore
        )

        if not existing_role:
            await interaction.response.send_message(
                "You do not have a color role!", ephemeral=True
            )
            logging.info("/color-role reset halted due to nonexisting color role")
            return

        await existing_role.edit(color=discord.Color(int("000000", 16)))
        logging.info("Role %s exists and has been reset", existing_role.name)
        await interaction.response.send_message(
            "Your role's color has been reset.", ephemeral=True
        )

    @role_assign_group.command(
        name="reassign",
        description="Checks if you are missing your role and reassigns it if so",
    )
    async def reassign(self, interaction: discord.Interaction) -> None:
        """
        Check if the user is missing their role, and reassign it if so.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        """

        logging.info("/color-role reassign invoked by %s", interaction.user)

        existing_role = find_existing_role(
            create_role_name(interaction.user), interaction.guild.roles  # type: ignore
        )

        if not existing_role:
            await interaction.response.send_message(
                "You do not have a color role.", ephemeral=True
            )
            logging.info(
                "/color-role reassign halted due to user not having a color role"
            )
            return

        if existing_role in interaction.user.roles:  # type: ignore
            await interaction.response.send_message(
                "You already have your color role.", ephemeral=True
            )
            logging.info("User already has their color role")
            return

        await interaction.user.add_roles(existing_role)  # type: ignore
        await interaction.response.send_message(
            "Your role has been reassigned.", ephemeral=True
        )
        logging.info(
            "Role %s exists and has been reassigned to %s",
            existing_role.name,
            interaction.user,
        )


async def setup(bot: commands.Bot):
    """
    Set up the ColorRoleCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(ColorRoleCog(bot))
