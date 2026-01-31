"""Fun commands."""

import logging
import secrets

import discord
from discord import app_commands
from discord.ext import commands

from ....util.http import ApiError
from ....util.log_handler import cog_setup_log_msg, log_app_command
from ...interaction import (
    build_response_embed,
    report,
    safe_send,
)
from ...ui import COIN_HEADS_COLOR, COIN_TAILS_COLOR
from ...ui.emoji import Status, Visual
from ..help import help_info
from .animal_tools import AnimalCarouselView, build_animal_embed
from .inaturalist_api import (
    ImageFetchAmount,
    animal_kind_autocomplete,
    fetch_inat_animal,
)

__author__ = "Gavin Borne"
__license__ = "MIT"

_FIZZBUZZ_PREVIEW_SIZE = 15
_FIZZBUZZ_MAX_ITERS = 100_000


def _fizzbuzz(n: int, /) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


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
    @help_info("Fun")
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
    @help_info(
        "Fun",
        notes=(
            "If a user is not provided, the command will get *your* profile picture!",
        ),
    )
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

        await interaction.response.send_message(embed=embed, file=icon, ephemeral=False)

    @app_commands.command(name="banner", description="Get a user's profile banner")
    @app_commands.describe(user="User to get the profile banner of")
    @help_info(
        "Fun",
        notes=("If a user is not provided, the command will get *your* banner!",),
    )
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

        await interaction.response.send_message(embed=embed, file=icon, ephemeral=False)

    @app_commands.autocomplete(kind=animal_kind_autocomplete)
    @app_commands.command(
        name="animal", description="Get animal picture(s) (and maybe a fact)!"
    )
    @app_commands.describe(
        kind="Which animal to fetch "
        "(wait for the autocomplete to pick the best-fitting option)",
        amount="How many images to fetch",
    )
    @help_info(
        "Fun",
        params={
            "kind": "What kind of animal to get photo(s) of",
        },
        notes=(
            (
                "After typing the kind of animal you want, waiting for a few seconds "
                "will reveal some autocomplete options that best match what you typed. "
                "Choosing one of these options can help guarantee "
                "your search returns what you want!"
            ),
        ),
    )
    async def animal(
        self,
        interaction: discord.Interaction,
        kind: str,
        amount: ImageFetchAmount = 1,
    ) -> None:
        """Get random animal images and possibly a fact."""
        log_app_command(interaction)

        await interaction.response.defer(thinking=True)

        try:
            result = await fetch_inat_animal(kind, images=amount)
            description_parts = []
            if result.fact:
                description_parts.append(result.fact)
            if result.source:
                description_parts.append(f"*Source: {result.source}*")
            description = (
                "\n\n".join(description_parts) if description_parts else "Here you go!"
            )

            embed, files = await build_animal_embed(result, description, 0)
            view = AnimalCarouselView(
                user=interaction.user, data=result, embed_description=description
            )
            await view.send(interaction, embed=embed, files=files, ephemeral=False)
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

    @app_commands.command(name="fizzbuzz", description="Perform the FizzBuzz algorithm")
    @app_commands.describe(
        iterations="The number of iterations to run the algorithm for",
        start="Optional starting number",
    )
    @help_info("Fun", notes=("`start` defaults to 1 if it is not provided.",))
    async def fizzbuzz(
        self, interaction: discord.Interaction, iterations: int, start: int = 1
    ) -> None:
        """Perform the FizzBuzz algorithm and return stats on it."""
        log_app_command(interaction)

        if iterations > _FIZZBUZZ_MAX_ITERS:
            await report(
                interaction,
                f"Please input a number lower than {_FIZZBUZZ_MAX_ITERS + 1}.",
                Status.FAILURE,
            )
            return

        out = [_fizzbuzz(n) for n in range(start, iterations + 1)]
        fizz_count = out.count("Fizz")
        buzz_count = out.count("Buzz")
        fb_count = out.count("FizzBuzz")
        number_count = iterations - fizz_count - buzz_count - fb_count

        if len(out) > 2 * _FIZZBUZZ_PREVIEW_SIZE:
            head = out[:_FIZZBUZZ_PREVIEW_SIZE]
            tail = out[-_FIZZBUZZ_PREVIEW_SIZE:]
            out = [*head, "...", *tail]

        embed, icon = build_response_embed(
            title=f"{Visual.SODA} FizzBuzz",
            description=(
                "Here's the result of running FizzBuzz with "
                f"**{iterations}** iterations starting at **{start}**."
            ),
        )
        embed.add_field(name="Fizz Count", value=fizz_count)
        embed.add_field(name="Buzz Count", value=buzz_count)
        embed.add_field(name="FizzBuzz Count", value=fb_count)
        embed.add_field(name="Number Count", value=number_count)

        embed.add_field(name="Algorithm Results", value="\n".join(out), inline=False)

        await safe_send(interaction, embed=embed, file=icon, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(FunCog(bot))
