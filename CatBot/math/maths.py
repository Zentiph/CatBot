"""
maths.py
Code for mathematical operations/functions to be used for CatBot's math-related commands.
"""

import logging
import math
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


# pylint: disable=too-many-public-methods
class MathCog(commands.Cog, name="Math Commands"):
    """
    Cog containing math commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("MathCog loaded")

    dist_group = app_commands.Group(
        name="distance",
        description="Calculate the distance between two points.",
    )

    bulk_group = app_commands.Group(  # TODO:
        name="bulk",
        description="Versions of math commands designed to take bulk inputs.",
    )

    @app_commands.command(name="add", description="Add two numbers")
    @app_commands.describe(x="First number", y="Second number")
    async def add(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
    ) -> None:
        """
        Add `x` and `y`.
        """

        logging.info("/add x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"{x} + {y} = {x + y}")

    @app_commands.command(name="sub", description="Subtract two numbers")
    @app_commands.describe(x="First number", y="Second number")
    async def sub(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
    ) -> None:
        """
        Subtract `x` and `y`.
        """

        logging.info("/sub x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"{x} - {y} = {x - y}")

    @app_commands.command(name="mul", description="Multiply two numbers")
    @app_commands.describe(x="First number", y="Second number")
    async def mul(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
    ) -> None:
        """
        Multiply `x` and `y`.
        """

        logging.info("/mul x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"{x} * {y} = {x * y}")

    @app_commands.command(name="div", description="Divide two numbers")
    @app_commands.describe(x="First number", y="Second number")
    async def div(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
    ) -> None:
        """
        Divide `x` and `y`.
        """

        logging.info("/div x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"{x} / {y} = {x / y}")

    @app_commands.command(
        name="floordiv", description="Divide two numbers and floor the result"
    )
    @app_commands.describe(x="First number", y="Second number")
    async def floordiv(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
    ) -> None:
        """
        Divide `x` and `y` and floor the result.
        """

        logging.info("/floordiv x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"{x} // {y} = {x // y}")

    @app_commands.command(
        name="pow", description="Raise a number to the power of another"
    )
    @app_commands.describe(x="Base number", y="Exponent number")
    async def pow(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
    ) -> None:
        """
        Raise `x` to the power of `y`.
        """

        logging.info("/pow x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"{x} ^ {y} = {x**y}")

    @app_commands.command(
        name="mod", description="Calculate the modulus of two numbers"
    )
    @app_commands.describe(x="First number", y="Second number")
    async def mod(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
    ) -> None:
        """
        Calculate the modulus of `x` and `y`.
        """

        logging.info("/mod x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"{x} % {y} = {x % y}")

    @app_commands.command(
        name="sqrt", description="Calculate the square root of a number"
    )
    @app_commands.describe(x="Number to calculate the square root of")
    async def sqrt(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the square root of `x`.
        """

        logging.info("/sqrt x=%s invoked by %s", x, interaction.user)
        await interaction.response.send_message(f"sqrt({x}) = {math.sqrt(x)}")

    @app_commands.command(
        name="cbrt", description="Calculate the cube root of a number"
    )
    @app_commands.describe(x="Number to calculate the cube root of")
    async def cbrt(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the cube root of `x`.
        """

        logging.info("/cbrt x=%s invoked by %s", x, interaction.user)
        await interaction.response.send_message(f"cbrt({x}) = {math.cbrt(x)}")

    @app_commands.command(
        name="nroot", description="Calculate the nth root of a number"
    )
    @app_commands.describe(x="Number to calculate the nth root of", n="Root number")
    async def nroot(
        self,
        interaction: discord.Interaction,
        x: float,
        n: float,
    ) -> None:
        """
        Calculate the `n`th root of `x`.
        """

        logging.info("/nroot x=%s n=%s invoked by %s", x, n, interaction.user)
        await interaction.response.send_message(f"{n}root({x}) = {x ** (1 / n)}")

    @app_commands.command(
        name="abs", description="Calculate the absolute value of a number"
    )
    @app_commands.describe(x="Number to calculate the absolute value of")
    async def abs(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the absolute value of `x`.
        """

        logging.info("/abs x=%s invoked by %s", x, interaction.user)
        await interaction.response.send_message(f"abs({x}) = {abs(x)}")

    @app_commands.command(name="ceil", description="Calculate the ceiling of a number")
    @app_commands.describe(x="Number to calculate the ceiling of")
    async def ceil(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the ceiling of `x`.
        """

        logging.info("/ceil x=%s invoked by %s", x, interaction.user)
        await interaction.response.send_message(f"ceil({x}) = {math.ceil(x)})")

    @app_commands.command(name="floor", description="Calculate the floor of a number")
    @app_commands.describe(x="Number to calculate the floor of")
    async def floor(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the floor of `x`.
        """

        logging.info("/floor x=%s invoked by %s", x, interaction.user)
        await interaction.response.send_message(f"floor({x}) = {math.floor(x)})")

    @app_commands.command(
        name="round", description="Round a number to the specified number of digits"
    )
    @app_commands.describe(x="Number to round", ndigits="Number of digits to round to")
    async def round_(
        self, interaction: discord.Interaction, x: float, ndigits: int = 0
    ) -> None:
        """
        Round `x` to `ndigits`.
        """

        logging.info(
            "/round x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )
        await interaction.response.send_message(
            f"{x} rounded to {ndigits} decimal places: {round(x, ndigits)})"
        )

    @app_commands.command(name="log", description="Calculate the logarithm of a number")
    @app_commands.describe(
        x="Number to calculate the logarithm of",
        base="Base of the logarithm; if empty, defaults to base e (natural logarithm)",
    )
    async def log(
        self,
        interaction: discord.Interaction,
        x: float,
        base: Optional[float] = None,
    ) -> None:
        """
        Calculate the logarithm base `base` of `x`.
        """

        logging.info("/log x=%s base=%s invoked by %s", x, base, interaction.user)

        if base is None:
            result = math.log(x)
            await interaction.response.send_message(f"ln({x}) = {result}")
            return

        result = math.log(x, base)
        await interaction.response.send_message(f"log{base}({x}) = {result}")

    @app_commands.command(
        name="gcd",
        description="Calculate the greatest common divisor/denominator (GCD) of two numbers",
    )
    @app_commands.describe(x="First number", y="Second number")
    async def gcd(
        self,
        interaction: discord.Interaction,
        x: int,
        y: int,
    ) -> None:
        """
        Calculate the greatest common divisor of `x` and `y`.
        """

        logging.info("/gcd x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"gcd({x}, {y}) = {math.gcd(x, y)}")

    @app_commands.command(
        name="lcm",
        description="Calculate the least common multiplier (LCM) of two numbers",
    )
    @app_commands.describe(x="First number", y="Second number")
    async def lcm(
        self,
        interaction: discord.Interaction,
        x: int,
        y: int,
    ) -> None:
        """
        Calculate the least common multiplier of `x` and `y`.
        """

        logging.info("/lcm x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"lcm({x}, {y}) = {math.lcm(x, y)}")

    @dist_group.command(
        name="cartesian-2d",
        description="Calculate the Cartesian distance between two points in 2D space",
    )
    @app_commands.describe(
        x1="First x-coordinate",
        y1="First y-coordinate",
        x2="Second x-coordinate",
        y2="Second y-coordinate",
    )
    async def distance_cartesian_2d(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> None:
        """
        Calculate the Cartesian distance between two points in 2D.
        """

        logging.info(
            "/distance cartesian-2d x1=%s y1=%s x2=%s y2=%s invoked by %s",
            x1,
            y1,
            x2,
            y2,
            interaction.user,
        )

        await interaction.response.send_message(
            f"distance(({x1}, {y1}), ({x2}, {y2})) = {
                math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            }"
        )

    @dist_group.command(
        name="cartesian-3d",
        description="Calculate the Cartesian distance between two points in 3D space",
    )
    @app_commands.describe(
        x1="First x-coordinate",
        y1="First y-coordinate",
        z1="First z-coordinate",
        x2="Second x-coordinate",
        y2="Second y-coordinate",
        z2="Second z-coordinate",
    )
    async def distance_cartesian_3d(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        x1: float,
        y1: float,
        z1: float,
        x2: float,
        y2: float,
        z2: float,
    ) -> None:
        """
        Calculate the Cartesian distance between two 3D points.
        """

        logging.info(
            "/distance cartesian-3d x1=%s y1=%s z1=%s x2=%s y2=%s z2=%s invoked by %s",
            x1,
            y1,
            z1,
            x2,
            y2,
            z2,
            interaction.user,
        )

        await interaction.response.send_message(
            f"distance(({x1}, {y1}, {z1}), ({x2}, {y2}, {z2})) = {
                math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            }"
        )

    @app_commands.command(
        name="factorial", description="Calculate the factorial of a number"
    )
    @app_commands.describe(x="Number to calculate the factorial of")
    async def factorial(self, interaction: discord.Interaction, x: int) -> None:
        """
        Calculate the factorial of a number.
        """

        logging.info("/factorial x=%s invoked by %s", x, interaction.user)

        if x < 0:
            await interaction.response.send_message(
                "Factorial is not defined for negative numbers.", ephemeral=True
            )
            return

        await interaction.response.send_message(f"factorial({x}) = {math.factorial(x)}")


async def setup(bot: commands.Bot):
    """
    Set up the MathCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(MathCog(bot))
