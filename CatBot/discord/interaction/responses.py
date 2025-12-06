"""Tools for responding to users."""

import discord

from ..ui import DEFAULT_EMBED_COLOR
from ..ui.emoji import Status

__author__ = "Gavin Borne"
__license__ = "MIT"


class InvalidImageFormatError(ValueError):
    """Raised if an invalid image type is used as a file attachment."""

    def __init__(self) -> None:
        """Create a new InvalidImageFormatError."""
        super().__init__("Image format should be .jpg or .png")


async def report(
    interaction: discord.Interaction,
    message: str,
    status: Status,
    /,
    *,
    ephemeral: bool = True,
) -> None:
    """Report a result of a command with a status emoji.

    Args:
        interaction (discord.Interaction): The interaction instance.
        message (str): The message to report.
        status (Status): The status.
        ephemeral (bool, optional): Whether to make the response ephemeral.
            Defaults to True.
    """
    await interaction.response.send_message(f"{status} {message}", ephemeral=ephemeral)


def generate_response_embed(
    *,
    title: str | None = None,
    description: str | None = None,
    color: int | discord.Color | None = DEFAULT_EMBED_COLOR,
    author: str | None = "CatBot",
    icon_filepath: str = "static/images/profile.jpg",  # TODO: see if this path works
    icon_filename: str = "image.png",
) -> tuple[discord.Embed, discord.File]:
    """Generate an embed, returning it and its required icon file.

    Args:
        title (Any | None): The title of the embed. Defaults to None.
        description (Any | None): The description of the embed. Defaults to None.
        color (int | discord.Color | None, optional): The The color of the embed.
            Defaults to DEFAULT_EMBED_COLOR.
        author (Any | None): The author of the embed. Defaults to "CatBot".
        icon_filepath (str): The filepath to the icon.
            Defaults to "static/images/profile.jpg".
        icon_filename (str): The filename of the icon. Defaults to "image.png".

    Returns:
        tuple[discord.Embed, discord.File]: The embed created and the icon file.
    """
    if not any(
        (
            icon_filepath.endswith("jpg"),
            icon_filepath.endswith(".jpeg"),
            icon_filepath.endswith(".png"),
        )
    ):
        raise InvalidImageFormatError()

    file = discord.File(icon_filepath, filename=icon_filename)
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name=author, icon_url=f"attachment://{icon_filename}")

    return embed, file
