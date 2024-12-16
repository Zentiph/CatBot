"""
fun.py
Fun commands for CatBot.
"""

#  * mini games (tic tac toe, etc)
#  * /cat-pic

import logging
import random
from datetime import datetime
from io import BytesIO
from platform import platform
from sys import version_info
from typing import List, Optional

import discord
import requests
from discord import app_commands
from discord.ext import commands
from psutil import Process

from ..bot_init import CAT_API_SEARCH_LINK, VERSION, get_cat_api_key_from_env
from ..help import PRIVATE, PUBLIC
from ..internal_utils import START_TIME, generate_authored_embed_with_icon

# A bit redundant, but helps readability.
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
MICROSECONDS_PER_SECOND = 1000000

CAT_API_KEY = get_cat_api_key_from_env()


def get_dependencies() -> str:
    """
    Get the dependencies used by CatBot.

    :return: A string representation of the dependencies used by CatBot
    :rtype: str
    """

    dependencies: List[str] = []
    with open("requirements.txt", encoding="utf8") as file:
        for line in file:
            dependencies.append(line.strip())
    return ", ".join(dependencies)


# pylint: disable=too-many-public-methods
class FunCog(commands.Cog, name="Fun Commands"):
    """
    Cog containing fun commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("FunCog loaded")

    @app_commands.command(name="stats", description="Get stats about the bot")
    async def stats(self, interaction: discord.Interaction) -> None:
        """
        Report general stats about the bot.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        """

        logging.info("/stats invoked by %s", interaction.user)

        await interaction.response.defer(thinking=True)

        servers = str(len(self.bot.guilds))
        uptime = datetime.now() - START_TIME
        days = uptime.days
        # We use modulo here to make sure the number of hours is less than 24,
        # essentially ignoring all hours except for the ones left over after the days.
        hours = (uptime.seconds // SECONDS_PER_HOUR) % HOURS_PER_DAY
        # We do the same thing here with minutes as well.
        minutes = (uptime.seconds // SECONDS_PER_MINUTE) % MINUTES_PER_HOUR
        # And seconds.
        seconds = uptime.seconds % SECONDS_PER_MINUTE
        # And microseconds.
        microseconds = uptime.microseconds % MICROSECONDS_PER_SECOND

        memory_usage = Process().memory_info().rss / 1024**2  # bytes -> MiB
        host = platform()
        python_version = (
            f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        )
        discord_py_version = (
            f"{discord.version_info.major}.{discord.version_info.minor}"
            + f".{discord.version_info.micro}"
        )

        embed, icon = generate_authored_embed_with_icon(
            embed_title="CatBot Stats",
            embed_description="Here's some statistics about myself.",
        )
        embed.add_field(name="Version", value=VERSION)
        embed.add_field(name="Servers", value=servers)
        embed.add_field(
            name="Uptime",
            value=f"{days} days, {hours} hours, {minutes} minutes, "
            + f"{seconds} seconds, {microseconds} microseconds",
            inline=False,
        )
        embed.add_field(name="Public Commands", value=len(PUBLIC))
        embed.add_field(name="Private Commands", value=len(PRIVATE))
        embed.add_field(
            name="Memory Usage", value=f"{round(memory_usage, 2)} MiB", inline=False
        )
        embed.add_field(name="Language", value="Python")
        embed.add_field(name="Language Version", value=python_version)
        embed.add_field(name="Package", value="discord.py")
        embed.add_field(name="Package Version", value=discord_py_version)
        embed.add_field(name="Dependencies", value=get_dependencies())
        embed.add_field(name="Host", value=host, inline=False)

        await interaction.followup.send(embed=embed, file=icon)

    # While this is a random command, it's more fun as it uses
    # custom images and is more generally used.
    # Also, since most fun commands aren't grouped,
    # this is easier to find which is ideal.
    @app_commands.command(name="flip-coin", description="Flip a coin")
    async def flip_coin(self, interaction: discord.Interaction) -> None:
        """
        Flip a coin.
        """

        logging.info("/flip-coin invoked by %s", interaction.user)

        heads = random.randint(0, 1)

        if heads:
            embed, icon = generate_authored_embed_with_icon(
                embed_title="Coin Flip",
                embed_description="Here's the result of your coin flip.",
                embed_color=discord.Color.from_rgb(255, 200, 95),  # Heads coin color
            )
            coin = discord.File(fp="CatBot/images/coin_heads.png", filename="coin.png")
        else:
            embed, icon = generate_authored_embed_with_icon(
                embed_title="Coin Flip",
                embed_description="Here's the result of your coin flip.",
                embed_color=discord.Color.from_rgb(203, 203, 203),  # Tails coin color
            )
            coin = discord.File(fp="CatBot/images/coin_tails.png", filename="coin.png")

        embed.set_image(url="attachment://coin.png")

        await interaction.response.send_message(embed=embed, files=(coin, icon))

    @app_commands.command(
        name="profile-picture", description="Get a user's profile picture"
    )
    @app_commands.describe(user="User to get the profile picture of")
    async def profile_picture(
        self, interaction: discord.Interaction, user: Optional[discord.User] = None
    ) -> None:
        """
        Get a user's profile picture.
        """

        logging.info("/profile-picture user=%s invoked by %s", user, interaction.user)

        if user is None:
            user = interaction.user  # type: ignore

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{user.display_name}'s Profile Picture",  # type: ignore
            embed_description=f"Here's {user.display_name}'s profile picture.",  # type: ignore
        )
        embed.set_image(url=user.display_avatar.url)  # type: ignore

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.command(name="banner", description="Get a user's profile banner")
    @app_commands.describe(user="User to get the profile banner of")
    async def banner(
        self, interaction: discord.Interaction, user: Optional[discord.User] = None
    ) -> None:
        """
        Get a user's profile banner.
        """

        logging.info("/banner user=%s invoked by %s", user, interaction.user)

        if user is None:
            user = interaction.user  # type: ignore

        if user.banner is None:  # type: ignore
            await interaction.response.send_message(
                f"{user.display_name} does not have a banner.", ephemeral=True  # type: ignore
            )
            return

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{user.display_name}'s Profile Banner",  # type: ignore
            embed_description=f"Here's {user.display_name}'s profile banner.",  # type: ignore
        )
        embed.set_image(url=user.banner.url)  # type: ignore

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.command(name="cat-pic", description="Get a random cat picture")
    async def cat_pic(self, interaction: discord.Interaction) -> None:
        """
        Get a random cat picture from the Cat API.
        """

        logging.info("/cat-pic invoked by %s", interaction.user)

        await interaction.response.defer(thinking=True)

        response = requests.get(
            CAT_API_SEARCH_LINK, headers={"x-api-key": CAT_API_KEY}, timeout=10
        )

        if response.status_code != 200:
            logging.warning(
                "Failed to fetch site data: status code %s", response.status_code
            )
            await interaction.followup.send(
                "Failed to fetch site data. "
                + "Please contact @zentiph to report this if the issue persists.",
                ephemeral=True,
            )
            return

        data = response.json()
        if not data:
            logging.warning("No images found in the response")
            await interaction.followup.send(
                "No images were found. Please contact @zentiph if this issue persists.",
                ephemeral=True,
            )
            return

        image_url = data[0]["url"]
        image_response = requests.get(image_url, timeout=10)

        if image_response.status_code != 200:
            logging.warning(
                "Failed to fetch image data: status code %s", response.status_code
            )
            await interaction.followup.send(
                "Failed to fetch image data. "
                + "Please contact @zentiph to report this if the issue persists.",
                ephemeral=True,
            )
            return

        image_bytes = BytesIO(image_response.content)
        filename = "cat.png"
        file = discord.File(fp=image_bytes, filename=filename)

        embed, icon = generate_authored_embed_with_icon(
            embed_title="Random Cat Picture",
            embed_description="Here's your random cat picture.",
        )
        embed.set_image(url=f"attachment://{filename}")

        await interaction.followup.send(embed=embed, files=(file, icon))


async def setup(bot: commands.Bot):
    """
    Set up the FunCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(FunCog(bot))
