"""Tools for responding to users."""

from collections.abc import Sequence
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import discord
from discord.utils import MISSING

from ..ui import DEFAULT_EMBED_COLOR
from ..ui.emoji import Status

__author__ = "Gavin Borne"
__license__ = "MIT"


file_cache: dict[str, bytes] = {}


@dataclass(frozen=True)
class GuildInteractionData:
    """Interaction data to track when in a guild."""

    member: discord.Member
    """The member that spawned the interaction."""
    guild: discord.Guild
    """The guild in which the interaction was spawned."""


class InvalidImageFormatError(ValueError):
    """Raised if an invalid image type is used as a file attachment."""

    def __init__(self, message: str = "", /) -> None:
        """Raised if an invalid image type is used as a file attachment."""
        super().__init__(message or "Image format should be .jpg or .png")


async def safe_send(
    interaction: discord.Interaction,
    /,
    content: str | None = None,
    *,
    ephemeral: bool = True,
    embed: discord.Embed = MISSING,
    embeds: Sequence[discord.Embed] = MISSING,
    view: discord.ui.View = MISSING,
    file: discord.File = MISSING,
    files: Sequence[discord.File] = MISSING,
    delete_after: float | None = None,
) -> discord.Message | None:
    """Safely send a response to an interaction, handling double-responds.

    Args:
        interaction (discord.Interaction): The interaction instance to respond to.
        content (str | None, optional): The message content. If None, content is
            omitted for followup sends. Defaults to None.
        ephemeral (bool, optional): Whether the message should be ephemeral.
            Defaults to True.
        embed (discord.Embed, optional): A single embed to include. Defaults to
            MISSING.
        embeds (Sequence[discord.Embed], optional): Multiple embeds to include.
            Defaults to MISSING.
        view (discord.ui.View, optional): A view to attach to the message. Defaults
            to MISSING.
        file (discord.File, optional): A single file to include. Defaults to
            MISSING.
        files (Sequence[discord.File], optional): Multiple files to include.
            Defaults to MISSING.
        delete_after (float, optional): Delete the message after this many seconds.
            Defaults to None.

    Returns:
        discord.Message | None: The original response of the interaction if applicable.
    """
    try:
        await interaction.response.send_message(
            content,
            ephemeral=ephemeral,
            embed=embed,
            embeds=embeds,
            view=view,
            file=file,
            files=files,
            delete_after=delete_after,
        )
        return await interaction.original_response()
    except discord.InteractionResponded:
        if content is None:
            return await interaction.followup.send(
                ephemeral=ephemeral,
                embed=embed,
                embeds=embeds,
                view=view,
                file=file,
                files=files,
                wait=True,
            )
        return await interaction.followup.send(
            content,
            ephemeral=ephemeral,
            embed=embed,
            embeds=embeds,
            view=view,
            file=file,
            files=files,
            wait=True,
        )


async def safe_edit(
    interaction: discord.Interaction,
    /,
    *,
    content: str | None = None,
    embed: discord.Embed = MISSING,
    embeds: Sequence[discord.Embed] = MISSING,
    attachments: Sequence[discord.Attachment | discord.File] = MISSING,
    view: discord.ui.View = MISSING,
    allowed_mentions: discord.AllowedMentions = MISSING,
) -> None:
    """Safely edit the message associated with an interaction, handling response state.

    Args:
        interaction (discord.Interaction): The interaction instance whose message
            should be edited.
        content (str | None, optional): New message content. Defaults to None.
        embed (discord.Embed, optional): A single embed to set. Defaults to
            MISSING.
        embeds (Sequence[discord.Embed], optional): Multiple embeds to set.
            Defaults to MISSING.
        attachments (Sequence[discord.Attachment | discord.File], optional): New
            attachments for the message. Defaults to MISSING.
        view (discord.ui.View, optional): A view to attach/update on the message.
            Defaults to MISSING.
        allowed_mentions (discord.AllowedMentions, optional): Controls mention
            parsing for the edited message. Defaults to MISSING.

    Raises:
        discord.HTTPException: If Discord rejects the edit.
        discord.Forbidden: If the bot lacks permissions to edit the message.
    """
    try:
        await interaction.response.edit_message(
            content=content,
            embed=embed,
            embeds=embeds,
            attachments=attachments,
            view=view,
            allowed_mentions=allowed_mentions,
        )
    except discord.InteractionResponded:
        await interaction.edit_original_response(
            content=content,
            embed=embed,
            embeds=embeds,
            attachments=attachments,
            view=view,
            allowed_mentions=allowed_mentions,
        )


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
    await safe_send(interaction, f"{status} {message}", ephemeral=ephemeral)


def build_response_embed(
    *,
    title: str | None = None,
    description: str | None = None,
    color: int | discord.Color | None = DEFAULT_EMBED_COLOR,
    author: str | None = "CatBot",
    icon_filepath: str = "static/images/profile.jpg",
    icon_filename: str = "image.png",
) -> tuple[discord.Embed, discord.File]:
    """Build an embed, returning it and its required icon file.

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
    if Path(icon_filepath).suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise InvalidImageFormatError()

    data = file_cache.get(icon_filepath)
    if data is None:
        data = Path(icon_filepath).read_bytes()
        file_cache[icon_filepath] = data

    file = discord.File(BytesIO(data), filename=icon_filename)
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name=author, icon_url=f"attachment://{icon_filename}")

    return embed, file


def get_guild_interaction_data(
    interaction: discord.Interaction, /
) -> GuildInteractionData | None:
    """Get the necessary information needed for an interaction that occurs in a guild.

    Args:
        interaction (discord.Interaction): The interaction instance.

    Returns:
        GuildInteractionData | None: The guild interaction data,
            or None if the interaction did not happen in a guild.
    """
    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        return None
    return GuildInteractionData(member=interaction.user, guild=interaction.guild)
