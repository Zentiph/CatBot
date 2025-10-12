"""
internal_utils.py
Utilities for internal functions such as embed creation.
"""

from datetime import datetime
from typing import Any, Literal, Optional, Union, Tuple

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
def generate_authored_embed_with_icon(
    *,
    embed_title: Optional[Any] = None,
    embed_description: Optional[Any] = None,
    embed_color: Optional[Union[int, discord.Color]] = DEFAULT_EMBED_COLOR,
    embed_author_name: Optional[Any] = "CatBot",
    icon_filepath: str = "CatBot/images/profile.jpg",
    icon_filename: str = "image.png",
) -> Tuple[discord.Embed, discord.File]:
    """
    Generate an authored embed and the icon file required.

    :param embed_title: Title of the embed, defaults to None
    :type embed_title: Optional[Any], optional
    :param embed_description: Description of the embed, defaults to None
    :type embed_description: Optional[Any], optional
    :param embed_color: Color of the embed, defaults to DEFAULT_EMBED_COLOR
    :type embed_color: Optional[Union[int, discord.Color]], optional
    :param embed_author_name: Author of the embed, defaults to "CatBot"
    :type embed_author_name: Optional[Any], optional
    :param icon_filepath: Filepath to the icon, defaults to "CatBot/images/profile.jpg"
    :type icon_filepath: str, optional
    :param icon_filename: Filename of the icon, defaults to "image.png"
    :type icon_filename: str, optional
    :return: The embed and icon file in a tuple
    :rtype: Tuple[discord.Embed, discord.File]
    """

    if not any(
        (
            (
                icon_filepath.endswith(".jpg"),
                icon_filepath.endswith(".jpeg"),
                icon_filepath.endswith(".png"),
            )
        )
    ):
        raise ValueError("Image filepath should be a .jpg or .png file")

    file = discord.File(icon_filepath, filename=icon_filename)

    embed = discord.Embed(
        title=embed_title,
        description=embed_description,
        color=embed_color,
    )
    embed.set_author(name=embed_author_name, icon_url=f"attachment://{icon_filename}")

    return embed, file
