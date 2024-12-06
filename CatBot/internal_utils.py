"""
internal_utils.py
Utilities for internal functions such as embed creation.
"""

from datetime import datetime
from typing import Any, Literal, Optional, Union

import discord

# We redefine this here to prevent circular import
DEFAULT_EMBED_COLOR = discord.Color(int("ffffff", 16))
START_TIME = datetime.now()
TimeUnit = Literal["seconds", "minutes", "hours", "days"]
TIME_MULTIPLICATION_TABLE = {
    "seconds": 1,
    "minutes": 60,
    "hours": 3600,
    "days": 86400,
}


def generate_image_file(filepath: str) -> discord.File:
    """
    Generate an image File given `filepath`.
    The image's name is "image.png".

    :param filepath: Path to an image
    :type filepath: str
    :return: Discord image File
    :rtype: discord.File
    """

    if not any(
        (
            (
                filepath.endswith(".jpg"),
                filepath.endswith(".jpeg"),
                filepath.endswith(".png"),
            )
        )
    ):
        raise ValueError("Image filepath should be a .jpg or .png file")

    return discord.File(filepath, filename="image.png")


def wrap_reason(reason: str, caller: Union[discord.Member, discord.User]) -> str:
    """
    Wrap reason to include the caller's name and ID in the reason (for admin logging purposes).

    :param reason: Original reason string
    :type reason: str
    :param caller: Command caller
    :type caller: Union[discord.Member, discord.User]
    :return: Wrapped reason string
    :rtype: str
    """

    return f"@{caller.name} (ID={caller.id}): {reason}"


# pylint: disable=too-many-arguments
def generate_authored_embed(
    *,
    title: Optional[Any] = None,
    description: Optional[Any] = None,
    color: Optional[Union[int, discord.Color]] = DEFAULT_EMBED_COLOR,
    author_name: Optional[Any] = "CatBot",
    url: Optional[Any] = None,
    icon_url: Optional[Any] = "attachment://image.png",
) -> discord.Embed:
    """
    Generate an embed with provided title, description, color, and author information.

    :param title: Embed title, defaults to None
    :type title: Optional[Any], optional
    :param description: Embed description, defaults to None
    :type description: Optional[Any], optional
    :param color: Embed color, defaults to DEFAULT_EMBED_COLOR
    :type color: Optional[Union[int, discord.Color]], optional
    :param author_name: Author name, defaults to "CatBot"
    :type author_name: Optional[Any], optional
    :param url: Author URL, defaults to None
    :type url: Optional[Any], optional
    :param icon_url: Author icon URL, defaults to "CatBot/images/profile.jpg"
    :type icon_url: Optional[Any], optional
    :return: Authored embed
    :rtype: discord.Embed
    """

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
    )
    embed.set_author(name=author_name, url=url, icon_url=icon_url)

    return embed
