"""
date_time.py
Date and time related commands.
"""

import datetime
import logging
from typing import Literal

import discord
import pytz
from discord import app_commands
from discord.ext import commands

from ..CatBot_utils import emojis, generate_authored_embed_with_icon
from .dt_formatting import (
    NUMBER_TO_DAY,
    NUMBER_TO_MONTH,
    format_date,
    format_datetime,
    format_time,
)

INVALID_TIMEZONE_MESSAGE = (
    emojis.X
    + " You have entered an invalid timezone.\n"
    + "A list of valid timezones can be found here: "
    + "https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568",
)

Month = Literal[
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
Meridiem = Literal["AM", "PM"]


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
                INVALID_TIMEZONE_MESSAGE,
                ephemeral=True,
            )
            return

        timezone_location = [tz.lower() for tz in pytz.all_timezones].index(
            timezone.lower()
        )
        correct_spelling = pytz.all_timezones[timezone_location]

        found_datetime = datetime.datetime.now(pytz.timezone(correct_spelling))
        local_datetime = datetime.datetime.now()

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.STOPWATCH} Date & Time",
            embed_description="Here's the current date & time info you requested.",
        )
        embed.add_field(
            name=f"Given Time Zone Date & Time\n({correct_spelling})",
            value=format_datetime(found_datetime, military_time, seconds, microseconds),
        )
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
                INVALID_TIMEZONE_MESSAGE,
                ephemeral=True,
            )
            return

        timezone_location = [tz.lower() for tz in pytz.all_timezones].index(
            timezone.lower()
        )
        correct_spelling = pytz.all_timezones[timezone_location]

        found_date = datetime.datetime.now(pytz.timezone(correct_spelling)).date()
        local_datetime = datetime.datetime.now()
        local_date = local_datetime.date()

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.STOPWATCH} Date & Time",
            embed_description="Here's the current date & time info you requested.",
        )
        embed.add_field(
            name=f"Given Time Zone Date\n({correct_spelling})",
            value=format_date(found_date),
        )
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
                INVALID_TIMEZONE_MESSAGE,
                ephemeral=True,
            )
            return

        timezone_location = [tz.lower() for tz in pytz.all_timezones].index(
            timezone.lower()
        )
        correct_spelling = pytz.all_timezones[timezone_location]

        found_time = datetime.datetime.now(pytz.timezone(correct_spelling)).time()
        local_datetime = datetime.datetime.now()
        local_time = local_datetime.time()

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.STOPWATCH} Date & Time",
            embed_description="Here's the current date & time info you requested.",
        )
        embed.add_field(
            name=f"Given Time Zone Time\n({correct_spelling})",
            value=format_time(found_time, military_time, seconds, microseconds),
        )
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

    @datetime_group.command(name="weekday", description="Get the weekday of a date")
    @app_commands.describe(
        month="Month of the year", day="Day of the month", year="Year"
    )
    async def weekday(
        self, interaction: discord.Interaction, month: Month, day: int, year: int
    ) -> None:
        """
        Get the weekday based on the date given.
        """

        logging.info(
            "/date-time weekday month=%s day=%s year=%s invoked by %s",
            month,
            day,
            year,
            interaction.user,
        )

        try:
            date = datetime.date(year, NUMBER_TO_MONTH.index(month), day)
        except ValueError:  # Date creation failed due to invalid values
            await interaction.response.send_message(
                f"{emojis.X} Invalid date entered.", ephemeral=True
            )
            return

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.STOPWATCH} Weekday on {month} {day}, {year}",
            embed_description="Here's the weekday on the date you provided.",
        )
        embed.add_field(name="Weekday", value=NUMBER_TO_DAY[date.weekday()])

        await interaction.response.send_message(embed=embed, file=icon)

    @datetime_group.command(
        name="days-until",
        description="Find how many days are left until a certain date",
    )
    @app_commands.describe(
        month="Month of the year", day="Day of the month", year="Year"
    )
    async def days_until(
        self,
        interaction: discord.Interaction,
        month: Month,
        day: int,
        year: int,
    ) -> None:
        """
        Calculate the number of days until the specified date.
        """

        logging.info(
            "/date-time days-until month=%s day=%s year=%s invoked by %s",
            month,
            day,
            year,
            interaction.user,
        )

        await interaction.response.defer(thinking=True)

        try:
            date = datetime.date(year, NUMBER_TO_MONTH.index(month), day)
        except ValueError:  # Datetime creation failed due to invalid values
            await interaction.response.send_message(
                f"{emojis.X} Invalid date entered.", ephemeral=True
            )
            return

        now = datetime.datetime.now().date()
        delta = date - now

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.STOPWATCH} Day Difference",
            embed_description="Here's the number of days until the date you requested.",
        )
        embed.add_field(
            name=f"Days Until {month} {day}, {year}", value=f"{delta.days} days"
        )

        await interaction.followup.send(embed=embed, file=icon)


async def setup(bot: commands.Bot):
    """
    Set up the DateTimeCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(DateTimeCog(bot))
