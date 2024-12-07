"""
fun.py
Fun commands for CatBot.
"""

#  * Random something generator (int, float, etc)
#  * coin flip
#  * mini games (tic tac toe, etc)
#  * /time {timezone}
#  * /cat-pic
#  * /avatar {user}
#  * /banner {user}

import logging
import random

from sys import maxsize
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from ..internal_utils import generate_authored_embed

MAX_INT = maxsize
MIN_INT = -maxsize - 1


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

    random_group = app_commands.Group(
        name="random", description="Generate random values"
    )

    @random_group.command(name="integer", description="Generate a random integer")
    @app_commands.describe(
        a="The first endpoint",
        b="The second endpoint",
        seed="Optional seed to use when generating the value",
    )
    async def random_integer(
        self,
        interaction: discord.Interaction,
        a: int = 0,
        b: int = 10,
        seed: Optional[str] = None,
    ) -> None:
        """
        Generate a random integer in [`a`, `b`].

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param a: First endpoint, defaults to 0
        :type a: int, optional
        :param b: Second endpoint, defaults to 10
        :type b: int, optional
        :param seed: Optional seed to use when generating the value, defaults to None
        :type seed: Optional[str], optional
        """

        logging.info(
            "/random integer a=%s b=%s seed=%s invoked by %s",
            a,
            b,
            seed,
            interaction.user,
        )

        if a > b:
            await interaction.response.send_message(
                "The first endpoint cannot be greater than the second endpoint!",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        embed = generate_authored_embed(
            title="Random Integer",
            description="Here's your randomly generated integer.",
        )
        embed.add_field(
            name="Random Value",
            value=random.randint(a, b),
            inline=False,
        )
        embed.add_field(
            name="Interval",
            value=f"[{a}, {b}]",
            inline=False,
        )
        embed.add_field(
            name="Seed",
            value=seed,
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @random_group.command(
        name="decimal", description="Generate a random decimal number (float)"
    )
    @app_commands.describe(
        a="The first endpoint",
        b="The second endpoint",
        seed="Optional seed to use when generating the value",
    )
    async def random_decimal(
        self,
        interaction: discord.Interaction,
        a: float = 0.0,
        b: float = 1.0,
        seed: Optional[str] = None,
    ) -> None:
        """
        Generate a random decimal in [`a`, `b`].

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param a: First endpoint, defaults to None
        :type a: float, optional
        :param b: Second endpoint, defaults to None
        :type b: float, optional
        :param seed: Optional seed to use when generating the value, defaults to None
        :type seed: Optional[str], optional
        """

        logging.info(
            "/random decimal a=%s b=%s seed=%s invoked by %s",
            a,
            b,
            seed,
            interaction.user,
        )

        if a > b:
            await interaction.response.send_message(
                "The first endpoint cannot be greater than the second endpoint!",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        number = random.uniform(a, b)
        numerator, denominator = number.as_integer_ratio()

        embed = generate_authored_embed(
            title="Random Decimal",
            description="Here's your randomly generated decimal number.",
        )
        embed.add_field(name="Random Value", value=number)
        embed.add_field(name="As Fraction", value=f"{numerator} / {denominator}")
        embed.add_field(
            name="Interval",
            value=f"[{a}, {b}]",
            inline=False,
        )
        embed.add_field(
            name="Seed",
            value=seed,
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @random_group.command(
        name="choice",
        description="Choose a value from a list of values separated by commas",
    )
    @app_commands.describe(
        values="A list of values separated by commas",
        choices="Number of choices to make",
        duplicates="Whether duplicate choices are allowed",
        seed="Optional seed to use when generating the value",
    )
    async def random_choice(
        self,
        interaction: discord.Interaction,
        values: str,
        choices: int = 1,
        duplicates: bool = True,
        seed: Optional[str] = None,
    ) -> None:
        """
        Pick `choices` random items from `values`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param values: A list of values separated by commas
        :type values: str
        :param choices: The number of choices to make, defaults to 1
        :type choices: int
        :param duplicates: Whether duplicate choices are allowed, defaults to True
        :type duplicates: bool, optional
        :param seed: Optional seed to use when generating the value, defaults to None
        :type seed: Optional[str], optional
        """

        logging.info(
            "/random choice values=%s choices=%s duplicates=%s seed=%s invoked by %s",
            repr(values),
            choices,
            duplicates,
            seed,
            interaction.user,
        )

        values_list = values.split(",")

        if any(s == "" for s in values_list):
            await interaction.response.send_message(
                "Invalid input. Please provide a list of values separated by commas.",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        if duplicates:
            picked_choices = random.choices(values_list, k=choices)
        else:
            picked_choices = random.sample(values_list, k=choices)

        embed = generate_authored_embed(
            title="Random Choice(s)",
            description="Here's your randomly selected choice(s) from the values you gave.",
        )
        embed.add_field(
            name="Random Choice(s)",
            value=", ".join(picked_choices),
            inline=False,
        )
        embed.add_field(
            name="Original Values",
            value=", ".join(values_list),
            inline=False,
        )
        embed.add_field(
            name="Seed",
            value=seed,
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="shuffle",
        description="Shuffle a list of values separated by commas",
    )
    @app_commands.describe(
        values="A list of values separated by commas",
        seed="Optional seed to use when generating the value",
    )
    async def shuffle(
        self,
        interaction: discord.Interaction,
        values: str,
        seed: Optional[str] = None,
    ) -> None:
        """
        Shuffle `values`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param values: A list of values separated by commas
        :type values: str
        :param seed: Optional seed to use when generating the value, defaults to None
        :type seed: Optional[str], optional
        """

        logging.info(
            "/shuffle values=%s seed=%s invoked by %s",
            repr(values),
            seed,
            interaction.user,
        )

        values_list = values.split(",")
        original_values = values.split(",")

        if any(s == "" for s in values_list):
            await interaction.response.send_message(
                "Invalid input. Please provide a list of values separated by commas.",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        random.shuffle(values_list)

        embed = generate_authored_embed(
            title="Shuffled Values",
            description="Here's your randomly shuffled values from the values you gave.",
        )
        embed.add_field(
            name="Shuffled Values",
            value=", ".join(values_list),
            inline=False,
        )
        embed.add_field(
            name="Original Values",
            value=", ".join(original_values),
            inline=False,
        )
        embed.add_field(
            name="Seed",
            value=seed,
            inline=False,
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Set up the FunCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(FunCog(bot))
