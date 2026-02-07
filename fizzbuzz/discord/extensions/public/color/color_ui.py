"""Color Cog UI."""

from __future__ import annotations

import logging

import discord

from ....interaction import (
    add_new_role_to_member,
    build_response_embed,
    find_role,
    report,
    safe_edit,
    update_role_color,
)
from ....ui.emoji import Status, Visual
from ....views import RestrictedModal, RestrictedView
from .color_tools import CSS_COLOR_NAME_TO_HEX, Color3, generate_color_image

__author__ = "Gavin Borne"
__license__ = "MIT"


def build_color_embed(
    *, title: str, description: str, color: Color3
) -> tuple[discord.Embed, list[discord.File]]:
    """Build the /color response embed.

    Args:
        title (str): The title of the embed.
        description (str): The description of the embed.
        color (Color3): The color of the embed.

    Returns:
        tuple[discord.Embed, list[discord.File]]: _description_
    """
    hex6 = color.as_hex6()

    image = generate_color_image(color)
    filename = f"{hex6}.png"
    color_file = discord.File(fp=image, filename=filename)

    embed, icon = build_response_embed(
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

    name = CSS_COLOR_NAME_TO_HEX.get(hex6)
    if name:
        embed.add_field(name="Color Name", value=name)

    embed.set_image(url=f"attachment://{filename}")

    return embed, [color_file, icon]


def get_color_role_name(member: discord.Member, /) -> str:
    """Get the color role name for a given member.

    Args:
        member (discord.Member): The member.

    Returns:
        str: The color role name.
    """
    return f"{member.id}'s Color Role"


async def update_color_role(
    member: discord.Member,
    guild: discord.Guild,
    color: discord.Color,
    color_repr: str,
    interaction: discord.Interaction,
    logger: logging.Logger,
) -> None:
    """Set a member's color role.

    Args:
        member (discord.Member): The member whose role to update.
        guild (discord.Guild): The guild to update the color in.
        color (discord.Color): The new color.
        color_repr (str): A representation of the color to use in the response.
        interaction (discord.Interaction): The interaction instance.
        logger (logging.Logger): The logger to log with in case moving roles fails.
    """
    existing_role = find_role(get_color_role_name(member), guild)

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
        await add_new_role_to_member(member, get_color_role_name(member), color)
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
        logger.warning("Failed to create role due to lack of permissions")
    except discord.HTTPException:
        await report(interaction, "An error occurred. Please try again.", Status.ERROR)
        logger.exception("Failed to create role due to an unexpected error: %s")


class LightenModal(RestrictedModal["ColorView"]):
    """A modal for the user to enter an amount to brighten a color by."""

    amount: discord.ui.TextInput[LightenModal] = discord.ui.TextInput(
        label="Lighten amount (%)",
        placeholder="e.g. 20",
        min_length=1,
        max_length=3,
        required=True,
    )

    def __init__(self, view: ColorView) -> None:
        """A modal for the user to enter an amount to brighten a color by.

        Args:
            view (ColorView): The view that this modal spawned from.
        """
        super().__init__(view, title="Lighten Color")

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        """On user-submission, validate the percentage and apply it if possible.

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

        if percentage < 0:
            await report(
                interaction,
                "The percentage entered must be greater than 0%.",
                Status.FAILURE,
            )
            return

        percentage = min(percentage, 100)
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
    """A modal for the user to enter an amount to darken a color by."""

    amount: discord.ui.TextInput[DarkenModal] = discord.ui.TextInput(
        label="Darken amount (%)",
        placeholder="e.g. 20",
        min_length=1,
        max_length=3,
        required=True,
    )

    def __init__(self, view: ColorView) -> None:
        """A modal for the user to enter an amount to darken a color by.

        Args:
            view (ColorView): The view that this modal spawned from.
        """
        super().__init__(view, title="Darken Color")

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        """On user-submission, validate the percentage and apply it if possible.

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

        darkened = self.view.current_color.darken(percentage)
        self.view.current_color = darkened

        embed, files = build_color_embed(
            title=f"Darkened {percentage:.0f}% from "
            f"#{self.view.original_color.as_hex6()}",
            description="Here's your darkened color.",
            color=darkened,
        )

        await safe_edit(interaction, embed=embed, attachments=files, view=self.view)


class ColorView(RestrictedView):
    """A view for the /color embed, adding buttons to interact with the color."""

    def __init__(
        self,
        user: discord.abc.User,
        /,
        *,
        color: Color3,
        timeout: float | None = 60.0,
        in_server: bool,
    ) -> None:
        """A view for the /color embed, adding buttons to interact with the color.

        Args:
            user (discord.abc.User): The user who spawned the view.
            color (Color3): The original color chosen.
            in_server (bool): Whether this view was spawned in a server.
            timeout (float | None, optional): The timeout of the view in seconds.
                Defaults to 60.0.
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
        """Inverts the color when clicked.

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

    @discord.ui.button(label="Lighten", style=discord.ButtonStyle.primary, row=1)
    async def lighten_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Lightens the button when pressed, using a `LightenModal`.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        await interaction.response.send_modal(LightenModal(self))

    @discord.ui.button(label="Darken", style=discord.ButtonStyle.primary, row=1)
    async def darken_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Darkens the button when pressed, using a `DarkenModal`.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        await interaction.response.send_modal(DarkenModal(self))

    @discord.ui.button(
        label="Set As Color Role",
        style=discord.ButtonStyle.primary,
        row=2,
        # defaults to off,
        # is turned on in `__init__()`
        # if the interaction happened in a server
        disabled=True,
        custom_id="color:set_role",
    )
    async def set_as_role(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Sets this view's current color as the user's color role when pressed.

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
            logging.getLogger("ColorCog"),
        )

    @discord.ui.button(label="Revert", style=discord.ButtonStyle.secondary, row=2)
    async def revert_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button[ColorView]
    ) -> None:
        """Revert the view's color to its original color.

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
