"""Fun commands."""

from io import BytesIO
import logging
import secrets

import discord
from discord import app_commands
from discord.ext import commands

from ....util.http import ApiError, http_get_bytes
from ....util.pawprints import cog_setup_log_msg, log_app_command
from ...interaction import (
    build_response_embed,
    report,
    safe_send,
)
from ...ui import COIN_HEADS_COLOR, COIN_TAILS_COLOR
from ...ui.emoji import Status, Visual
from .inaturalist_api import (
    MAX_MULTI_IMAGE_FETCH_SIZE,
    AnimalResult,
    animal_kind_autocomplete,
    fetch_inat_animal,
)

__author__ = "Gavin Borne"
__license__ = "MIT"


MAX_FILENAME_LEN = 40
"""The maximum length of an attachment filename."""


logger = logging.getLogger("FunCog")


async def ensure_full_user(
    client: discord.Client, user: discord.Member | discord.User
) -> discord.User:
    """Ensure a user is packaged with the full data associated.

    Args:
        client (discord.Client): The client connection.
        user (discord.Member | discord.User): The user to get the full info of.

    Returns:
        discord.User: The full user payload.
    """
    return await client.fetch_user(user.id)


def safe_filename(filename: str) -> str:
    """Ensure a filename is safe by replacing risky characters with underscores.

    Args:
        filename (str): The filename to make safe.

    Returns:
        str: The safe filename.
    """
    keep = [c.lower() if c.isalnum() else "_" for c in filename]
    out = "".join(keep).strip("_")

    return out[:MAX_FILENAME_LEN] or "animal"


async def send_animal_embed(
    interaction: discord.Interaction, /, result: AnimalResult
) -> None:
    """Build and send an animal embed (for /animal).

    Args:
        interaction (discord.Interaction): The interaction instance.
        result (AnimalResult): The animal result from talking to iNaturalist.
    """
    urls = (result.images or [result.image_url])[:MAX_MULTI_IMAGE_FETCH_SIZE]

    description_parts = []
    if result.fact:
        description_parts.append(result.fact)
    if result.source:
        description_parts.append(f"*Source: {result.source}*")
    base_description = (
        "\n\n".join(description_parts) if description_parts else "Here you go!"
    )

    files: list[discord.File] = []
    embeds: list[discord.Embed] = []

    # build first embed once to get the icon
    first_filename = f"{safe_filename(result.kind)}_1.png"
    first_bytes = await http_get_bytes(urls[0], timeout=10)
    files.append(discord.File(fp=BytesIO(first_bytes), filename=first_filename))

    first_embed, icon = build_response_embed(
        title=f"{Visual.PAWS} Random {result.kind.title()} (1/{len(urls)})",
        description=base_description,
    )
    first_embed.set_image(url=f"attachment://{first_filename}")
    embeds.append(first_embed)

    # remaining images: no repeated icon creation
    for i, url in enumerate(urls[1:], start=2):
        image_bytes = await http_get_bytes(url, timeout=10)
        filename = f"{safe_filename(result.kind)}_{i}.png"
        files.append(discord.File(fp=BytesIO(image_bytes), filename=filename))

        e = discord.Embed(
            title=f"{Visual.PAWS} Random {result.kind.title()} ({i}/{len(urls)})",
            description="",
        )
        e.set_image(url=f"attachment://{filename}")
        embeds.append(e)

    files.append(icon)
    await safe_send(interaction, embeds=embeds, files=files)


class FunCog(commands.Cog, name="Fun Commands"):
    """Cog containing fun commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create the FunCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(name="coinflip", description="Flip a coin (50/50 odds)")
    async def coin_flip(self, interaction: discord.Interaction) -> None:
        """Flip a coin, returning an embed with custom coin images."""
        log_app_command(interaction)

        title = f"{Visual.COIN} Coin Flip"
        description = "Here's the result of your coin flip."

        heads = secrets.randbelow(2)  # 0 or 1
        if heads:
            embed, icon = build_response_embed(
                title=title, description=description, color=COIN_HEADS_COLOR
            )
            coin = discord.File(fp="static/images/coin_heads.png", filename="coin.png")
        else:
            embed, icon = build_response_embed(
                title=title, description=description, color=COIN_TAILS_COLOR
            )
            coin = discord.File(fp="static/images/coin_tails.png", filename="coin.png")

        embed.set_image(url="attachment://coin.png")

        await safe_send(interaction, embed=embed, files=(coin, icon), ephemeral=False)

    @app_commands.command(name="profile", description="Get a user's profile picture")
    @app_commands.describe(user="User to get the profile picture of")
    async def profile(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User | None = None,
    ) -> None:
        """Get a user's profile picture."""
        log_app_command(interaction)

        interaction_user = interaction.user
        target = user or interaction_user
        display_name = target.display_name

        embed, icon = build_response_embed(
            title=f"{Visual.PHOTO} {display_name}'s Profile Picture",
            description=f"Here's {display_name}'s profile picture.",
        )
        embed.set_image(url=target.display_avatar.url)

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.command(name="banner", description="Get a user's profile banner")
    @app_commands.describe(user="User to get the profile banner of")
    async def banner(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User | None = None,
    ) -> None:
        """Get a user's profile banner."""
        log_app_command(interaction)

        target = user or interaction.user
        # get the full user payload to ensure it has the banner info
        full_user = await ensure_full_user(interaction.client, target)

        if full_user.banner is None:
            await report(
                interaction,
                f"{full_user.display_name} does not have a banner.",
                Status.FAILURE,
            )
            return

        display_name = full_user.display_name

        embed, icon = build_response_embed(
            title=f"{Visual.PHOTO} {display_name}'s Profile Banner",
            description=f"Here's {display_name}'s profile banner.",
        )
        embed.set_image(url=full_user.banner.url)

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.autocomplete(kind=animal_kind_autocomplete)
    @app_commands.command(
        name="animal", description="Get an animal picture (and maybe a fact)!"
    )
    @app_commands.describe(
        kind="Which animal to fetch "
        "(wait for the autocomplete to pick the best-fitting option)",
        amount="How many images to fetch (1-5)",
    )
    async def animal(
        self, interaction: discord.Interaction, kind: str, amount: int = 1
    ) -> None:
        """Get a random animal image and possibly a fact."""
        log_app_command(interaction)

        await interaction.response.defer(thinking=True)

        try:
            amount = max(1, min(MAX_MULTI_IMAGE_FETCH_SIZE, amount))
            result = await fetch_inat_animal(kind, images=amount)
            await send_animal_embed(interaction, result)
        except ApiError as e:
            logger.warning("Animal API error: %s", e)
            await report(
                interaction,
                f"{e}\nPlease try again later, or submit a "
                "bug report if this keeps happening.",
                Status.ERROR,
            )
        except Exception:
            logger.exception("Unexpected error in /animal")
            await report(
                interaction,
                "Something went wrong.\nPlease try again later, or submit a "
                "bug report if this keeps happening.",
                Status.ERROR,
            )


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(FunCog(bot))
