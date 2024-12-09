"""
fun.py
Fun commands for CatBot.
"""

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

from ..internal_utils import generate_authored_embed, generate_image_file

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
                "The left endpoint cannot be greater than the right endpoint!",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        icon = generate_image_file("CatBot/images/profile.jpg")
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
                "The left endpoint cannot be greater than the right endpoint!",
                ephemeral=True,
            )
            return

        if seed is not None:
            random.seed(seed)

        number = random.uniform(a, b)
        numerator, denominator = number.as_integer_ratio()

        icon = generate_image_file("CatBot/images/profile.jpg")
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

        icon = generate_image_file("CatBot/images/profile.jpg")
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

        await interaction.response.send_message(embed=embed, file=icon)

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

        icon = generate_image_file("CatBot/images/profile.jpg")
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

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.command(name="flip-coin", description="Flip a coin")
    async def flip_coin(self, interaction: discord.Interaction) -> None:
        """
        Flip a coin.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        """

        logging.info("/flip-coin invoked by %s", interaction.user)

        heads = bool(random.randint(0, 1))

        icon = generate_image_file("CatBot/images/profile.jpg")

        if heads:
            embed = generate_authored_embed(
                title="Coin Flip",
                description="Here's the result of your coin flip.",
                color=discord.Color.from_rgb(255, 200, 95),  # Heads coin color
            )
            coin = generate_image_file(
                "CatBot/images/coin_heads.png", filename="coin.png"
            )
        else:
            embed = generate_authored_embed(
                title="Coin Flip",
                description="Here's the result of your coin flip.",
                color=discord.Color.from_rgb(203, 203, 203),  # Tails coin color
            )
            coin = generate_image_file(
                "CatBot/images/coin_tails.png", filename="coin.png"
            )

        embed.set_image(url="attachment://coin.png")

        await interaction.response.send_message(embed=embed, files=(coin, icon))


async def setup(bot: commands.Bot):
    """
    Set up the FunCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(FunCog(bot))
