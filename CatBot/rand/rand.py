"""
rand.py
Random commands for CatBot.
"""

import logging
import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from .. import emojis
from ..internal_utils import generate_authored_embed_with_icon


# pylint: disable=too-many-public-methods
class RandomCog(commands.Cog, name="Random Commands"):
    """
    Cog containing random commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("RandomCog loaded")

    random_group = app_commands.Group(
        name="random", description="Generate random values"
    )

    @random_group.command(name="integer", description="Generate a random integer")
    @app_commands.describe(
        a="The left endpoint",
        b="The right endpoint",
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
                f"{emojis.X} The left endpoint cannot be greater than the right endpoint!",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.RANDOM} Random Integer",
            embed_description="Here's your randomly generated integer.",
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

        await interaction.response.send_message(embed=embed, file=icon)

    @random_group.command(
        name="decimal", description="Generate a random decimal number (float)"
    )
    @app_commands.describe(
        a="The left endpoint",
        b="The right endpoint",
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
                f"{emojis.X} The left endpoint cannot be greater than the right endpoint!",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        number = random.uniform(a, b)
        numerator, denominator = number.as_integer_ratio()

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.RANDOM} Random Decimal",
            embed_description="Here's your randomly generated decimal number.",
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

        await interaction.response.send_message(embed=embed, file=icon)

    @random_group.command(
        name="choice",
        description="Choose a value from a list of values separated by commas",
    )
    @app_commands.describe(
        values="A list of values separated by commas",
        choices="Number of choices to make",
        duplicates="Whether duplicate choices are allowed",
        seed="Optional seed to use when generating the value(s)",
    )
    async def random_choice(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        values: str,
        choices: int = 1,
        duplicates: bool = True,
        seed: Optional[str] = None,
    ) -> None:
        """
        Pick `choices` random items from `values`.
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
                f"{emojis.X} Invalid input. Please provide a list of values separated by commas.",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        if duplicates:
            picked_choices = random.choices(values_list, k=choices)
        else:
            picked_choices = random.sample(values_list, k=choices)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.RANDOM} Random Choice(s)",
            embed_description="Here's your randomly selected choice(s) from the values you gave.",
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

        await interaction.response.send_message(embed=embed, file=icon)

    @random_group.command(
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
        """

        logging.info(
            "/random shuffle values=%s seed=%s invoked by %s",
            repr(values),
            seed,
            interaction.user,
        )

        values_list = values.split(",")
        original_values = values.split(",")

        if any(s == "" for s in values_list):
            await interaction.response.send_message(
                f"{emojis.X} Invalid input. Please provide a list of values separated by commas.",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        random.shuffle(values_list)

        embed, icon = generate_authored_embed_with_icon(
            embed_title=f"{emojis.RANDOM} Shuffled Values",
            embed_description="Here's your randomly shuffled values from the values you gave.",
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

        await interaction.response.send_message(embed=embed, file=icon)


async def setup(bot: commands.Bot):
    """
    Set up the RandomCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(RandomCog(bot))
