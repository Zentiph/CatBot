"""
stats.py
Code for CatBot's bot stats commands.
"""

import logging
from datetime import datetime
from platform import platform
from sys import version_info

import discord
from discord import app_commands
from discord.ext import commands
from psutil import Process

from ..bot_init import VERSION
from ..internal_utils import START_TIME, generate_authored_embed

# A bit redundant, but helps readability.
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
MICROSECONDS_PER_SECOND = 1000000


# pylint: disable=too-many-public-methods
class StatsCog(commands.Cog, name="Bot Stats Commands"):
    """
    Cog containing bot stats commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("StatsCog loaded")

    @app_commands.command(name="stats", description="Get stats about the bot")
    async def stats(self, interaction: discord.Interaction) -> None:
        """
        Report general stats about the bot.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        """

        logging.info("/stats invoked by %s", interaction.user)

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

        embed = generate_authored_embed(
            title="CatBot Stats", description="Here's some statistics about myself."
        )
        embed.add_field(name="Version", value=VERSION, inline=False)
        embed.add_field(
            name="Uptime",
            value=f"{days} days, {hours} hours, {minutes} minutes, "
            + f"{seconds} seconds, {microseconds} microseconds",
            inline=False,
        )
        embed.add_field(
            name="Memory Usage", value=f"{memory_usage:2f} MiB", inline=False
        )
        embed.add_field(name="Host", value=host, inline=False)
        # We use inline=True here to line up similar fields
        embed.add_field(name="Language", value="Python")
        embed.add_field(name="Python Version", value=python_version)
        embed.add_field(name="Package", value="discord.py", inline=False)
        embed.add_field(name="Package Version", value=discord_py_version)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Set up the StatsCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(StatsCog(bot))
