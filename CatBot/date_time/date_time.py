"""
times.py
Date and time related commands.
"""

import datetime
import logging

import discord
import pytz
from discord import app_commands
from discord.ext import commands

from ..internal_utils import generate_authored_embed, generate_image_file
from .dt_formatting import format_date, format_datetime, format_time


# pylint: disable=too-many-public-methods
class DateTimeCog(commands.Cog, name="Date & Time Commands"):
    """
    Cog containing date & time commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("DateTimeCog loaded")

    datetime_group = app_commands.Group(
        name="date-time", description="Get date and time information"
    )

    @datetime_group.command(
        name="date-time",
        description="Get the date and time in a timezone",
    )
    @app_commands.describe(
        timezone="The timezone to get the date and time in",
        military_time="Whether to use military (24-hour) time",
        seconds="Whether to include seconds",
        microseconds="Whether to include microseconds (automatically includes seconds as well)",
    )
    async def datetime_(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        timezone: str,
        military_time: bool = False,
        seconds: bool = False,
        microseconds: bool = False,
    ) -> None:
        """
        Get the date and time from `timezone`.
        """

        logging.info(
            "/date-time date-time timezone=%s military_time=%s "
            + "seconds=%s microseconds=%s invoked by %s",
            repr(timezone),
            military_time,
            seconds,
            microseconds,
            interaction.user,
        )

        # Defer in case lookups take too long
        await interaction.response.defer(thinking=True)

        timezone = timezone.strip()
        if timezone.lower() not in (tz.lower() for tz in pytz.all_timezones):
            await interaction.response.send_message(
                "You have entered an invalid timezone.\n"
                + "A list of valid timezones can be found here: "
                + "https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568",
                ephemeral=True,
            )
            return

        icon = generate_image_file("CatBot/images/profile.jpg")
        embed = generate_authored_embed(
            title="Date & Time",
            description="Here's the current date & time info you requested.",
        )

        timezone_location = [tz.lower() for tz in pytz.all_timezones].index(
            timezone.lower()
        )
        correct_spelling = pytz.all_timezones[timezone_location]

        found_datetime = datetime.datetime.now(pytz.timezone(correct_spelling))
        embed.add_field(
            name=f"Given Time Zone Date & Time\n({correct_spelling})",
            value=format_datetime(found_datetime, military_time, seconds, microseconds),
        )

        local_datetime = datetime.datetime.now()
        embed.add_field(
            name=f"Bot Local Date & Time\n({local_datetime.astimezone().tzname()})",
            value=format_datetime(local_datetime, military_time, seconds, microseconds),
        )
        embed.add_field(
            name="Time Specifications",
            value=f"24-Hour Time: {military_time}\nSeconds Included: "
            + f"{seconds or microseconds}\nMicroseconds Included: {microseconds}",
            inline=False,
        )

        await interaction.followup.send(embed=embed, file=icon)

    @datetime_group.command(
        name="date",
        description="Get the date in a timezone",
    )
    @app_commands.describe(
        timezone="The timezone to get the date in",
    )
    async def date(
        self,
        interaction: discord.Interaction,
        timezone: str,
    ) -> None:
        """
        Get the date from `timezone`.
        """

        logging.info(
            "/date-time date timezone=%s invoked by %s",
            repr(timezone),
            interaction.user,
        )

        await interaction.response.defer(thinking=True)

        timezone = timezone.strip()
        if timezone.lower() not in (tz.lower() for tz in pytz.all_timezones):
            await interaction.response.send_message(
                "You have entered an invalid timezone.\n"
                + "A list of valid timezones can be found here: "
                + "https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568",
                ephemeral=True,
            )
            return

        icon = generate_image_file("CatBot/images/profile.jpg")
        embed = generate_authored_embed(
            title="Date & Time",
            description="Here's the current date & time info you requested.",
        )

        timezone_location = [tz.lower() for tz in pytz.all_timezones].index(
            timezone.lower()
        )
        correct_spelling = pytz.all_timezones[timezone_location]

        found_date = datetime.datetime.now(pytz.timezone(correct_spelling)).date()
        embed.add_field(
            name=f"Given Time Zone Date\n({correct_spelling})",
            value=format_date(found_date),
        )

        local_datetime = datetime.datetime.now()
        local_date = local_datetime.date()
        embed.add_field(
            name=f"Bot Local Date\n({local_datetime.astimezone().tzname()})",
            value=format_date(local_date),
        )

        await interaction.followup.send(embed=embed, file=icon)

    @datetime_group.command(
        name="time",
        description="Get the time in a timezone",
    )
    @app_commands.describe(
        timezone="The timezone to get the time in",
        military_time="Whether to use military (24-hour) time",
        seconds="Whether to include seconds",
        microseconds="Whether to include microseconds (automatically includes seconds as well)",
    )
    async def time_(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        timezone: str,
        military_time: bool = False,
        seconds: bool = True,
        microseconds: bool = False,
    ) -> None:
        """
        Get the time from `timezone`.
        """

        logging.info(
            "/time timezone=%s military_time=%s seconds=%s microseconds=%s invoked by %s",
            repr(timezone),
            military_time,
            seconds,
            microseconds,
            interaction.user,
        )

        await interaction.response.defer(thinking=True)

        timezone = timezone.strip()
        if timezone.lower() not in (tz.lower() for tz in pytz.all_timezones):
            await interaction.response.send_message(
                "You have entered an invalid timezone.\n"
                + "A list of valid timezones can be found here: "
                + "https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568",
                ephemeral=True,
            )
            return

        icon = generate_image_file("CatBot/images/profile.jpg")
        embed = generate_authored_embed(
            title="Date & Time",
            description="Here's the current date & time info you requested.",
        )

        timezone_location = [tz.lower() for tz in pytz.all_timezones].index(
            timezone.lower()
        )
        correct_spelling = pytz.all_timezones[timezone_location]

        found_time = datetime.datetime.now(pytz.timezone(correct_spelling)).time()
        embed.add_field(
            name=f"Given Time Zone Time\n({correct_spelling})",
            value=format_time(found_time, military_time, seconds, microseconds),
        )

        local_datetime = datetime.datetime.now()
        local_time = local_datetime.time()
        embed.add_field(
            name=f"Bot Local Time\n({local_datetime.astimezone().tzname()})",
            value=format_time(local_time, military_time, seconds, microseconds),
        )
        embed.add_field(
            name="Time Specifications",
            value=f"24-Hour Time: {military_time}\nSeconds Included: "
            + f"{seconds or microseconds}\nMicroseconds Included: {microseconds}",
            inline=False,
        )

        await interaction.followup.send(embed=embed, file=icon)


async def setup(bot: commands.Bot):
    """
    Set up the DateTimeCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(DateTimeCog(bot))
