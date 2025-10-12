"""
stats.py
Code for statistical operations/functions to be used for CatBot's math-related commands.
"""

import logging
import statistics

import discord
from discord import app_commands
from discord.ext import commands

from ..CatBot_utils import emojis
from .math_utils import (
    create_sequence_string,
    generate_math_embed_with_icon,
    is_number,
    simplify_number_type,
)


# pylint: disable=too-many-public-methods
class StatisticsCog(commands.Cog, name="Probability and Statistics Commands"):
    """
    Cog containing stats commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("StatisticsCog loaded")

    stats_group = app_commands.Group(
        name="stats", description="Probability and statistics commands"
    )

    @stats_group.command(name="mean", description="Compute the mean of a set of values")
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def mean(self, interaction: discord.Interaction, numbers: str) -> None:
        """
        Find the mean of the provided numbers.
        """

        logging.info(
            "/stats mean numbers=%s invoked by %s", repr(numbers), interaction.user
        )

        await interaction.response.defer(thinking=True)

        numbers_list = numbers.replace(" ", "").split(",")
        if any(not is_number(num) for num in numbers_list):
            await interaction.followup.send(
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        sequence = create_sequence_string(numbers_list, ", ")
        result = simplify_number_type(
            statistics.fmean(float(num) for num in numbers_list)
        )

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of mean({sequence})", result_value=result
        )

        await interaction.followup.send(embed=embed, file=icon)

    @stats_group.command(
        name="median", description="Calculate the median of a set of values"
    )
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def median(
        self,
        interaction: discord.Interaction,
        numbers: str,
    ) -> None:
        """
        Find the median of the provided numbers.
        """

        logging.info(
            "/stats median numbers=%s invoked by %s", repr(numbers), interaction.user
        )

        await interaction.response.defer(thinking=True)

        numbers_list = numbers.replace(" ", "").split(",")
        if any(not is_number(num) for num in numbers_list):
            await interaction.followup.send(
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        sequence = create_sequence_string(numbers_list, ", ")
        result = simplify_number_type(
            statistics.median(float(num) for num in numbers_list)
        )

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of median({sequence})",
            result_value=result,
        )

        await interaction.followup.send(embed=embed, file=icon)

    @stats_group.command(
        name="mode", description="Calculate the first appearing mode of a set of values"
    )
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def mode(self, interaction: discord.Interaction, numbers: str) -> None:
        """
        Find the mode of the provided numbers.
        """

        logging.info(
            "/stats mode numbers=%s invoked by %s", repr(numbers), interaction.user
        )

        await interaction.response.defer(thinking=True)

        numbers_list = numbers.replace(" ", "").split(",")
        if any(not is_number(num) for num in numbers_list):
            await interaction.followup.send(
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        sequence = create_sequence_string(numbers_list, ", ")
        result = simplify_number_type(
            statistics.mode(float(num) for num in numbers_list)
        )

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of mode({sequence})",
            result_value=result,
        )

        await interaction.followup.send(embed=embed, file=icon)

    @stats_group.command(
        name="multimode", description="Calculate all the modes of a set of values"
    )
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def multimode(self, interaction: discord.Interaction, numbers: str) -> None:
        """
        Find the multimode of the provided numbers.
        """

        logging.info(
            "/stats multimode numbers=%s invoked by %s", repr(numbers), interaction.user
        )

        await interaction.response.defer(thinking=True)

        numbers_list = numbers.replace(" ", "").split(",")
        if any(not is_number(num) for num in numbers_list):
            await interaction.followup.send(
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        sequence = create_sequence_string(numbers_list, ", ")
        result = statistics.multimode(float(num) for num in numbers_list)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of multimode({sequence})",
            result_value=", ".join(str(simplify_number_type(r)) for r in result),
        )

        await interaction.followup.send(embed=embed, file=icon)


async def setup(bot: commands.Bot):
    """
    Set up the StatisticsCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(StatisticsCog(bot))
