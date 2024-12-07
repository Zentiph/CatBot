"""
maths.py
Code for mathematical operations/functions to be used for CatBot's math-related commands.
"""

import logging
import math
from re import match as re_match
from typing import Optional, Union

import discord
from discord import app_commands
from discord.ext import commands


def is_number(string: str) -> bool:
    """
    Determine if `string` is a valid number.
    """

    return bool(re_match(r"^-?\d+(\.\d+)?$", string))


def round_on_ndigits(
    x: Union[int, float, complex], ndigits: Optional[int], /
) -> Union[int, float, complex]:
    """
    Round `x` based on `ndigits` and return the result.

    :param x: Number to round
    :type x: Union[int, float, complex]
    :param ndigits: Number of digits to round, or None for no rounding
    :type ndigits: Optional[int]
    :return: The result of the rounding
    :rtype: Union[int, float, complex]
    """

    if ndigits is None:
        return x

    if isinstance(x, complex):
        return complex(round(x.real, ndigits), round(x.imag, ndigits))

    return round(x, ndigits)


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

        await interaction.response.send_message(f"{x} + {y} = **{x + y}**")

    @app_commands.command(
        name="sum", description="Sum up an arbitrary amount of numbers"
    )
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def sum(
        self,
        interaction: discord.Interaction,
        numbers: str,
    ) -> None:
        """
        Sum up the provided numbers.
        """

        logging.info("/sum numbers=%s invoked by %s", repr(numbers), interaction.user)

        numbers_list = numbers.replace(" ", "").split(
            ","
        )  # Split at commas and remove spaces
        if any(not is_number(num) for num in numbers_list):
            await interaction.response.send_message(
                "Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return
        total = sum(float(num) for num in numbers_list)

        await interaction.response.send_message(
            f"{" + ".join(numbers_list)} = **{total}**"
        )

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

        await interaction.response.send_message(f"{x} - {y} = **{x - y}**")

    @app_commands.command(name="mul", description="Multiply two numbers")
    @app_commands.describe(
        x="First number",
        y="Second number",
        ndigits="Number of digits to round the result by",
    )
    async def mul(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Multiply `x` and `y`.
        """

        logging.info(
            "/mul x=%s y=%s ndigits=%s invoked by %s", x, y, ndigits, interaction.user
        )

        result = round_on_ndigits(x + y, ndigits)

        await interaction.response.send_message(f"{x} * {y} = **{result}**")

    @app_commands.command(
        name="prod", description="Find the product of an arbitrary amount of numbers"
    )
    @app_commands.describe(
        numbers="An arbitrary amount of numbers separated by commas",
        ndigits="Number of digits to round the result by",
    )
    async def prod(
        self,
        interaction: discord.Interaction,
        numbers: str,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Find the product of the provided numbers.
        """

        logging.info(
            "/prod numbers=%s ndigits=%s invoked by %s",
            repr(numbers),
            ndigits,
            interaction.user,
        )

        numbers_list = numbers.replace(" ", "").split(
            ","
        )  # Split at commas and remove spaces
        if any(not is_number(num) for num in numbers_list):
            await interaction.response.send_message(
                "Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        result = round_on_ndigits(
            math.prod(float(num) for num in numbers_list), ndigits
        )

        await interaction.response.send_message(
            f"{" * ".join(numbers_list)} = **{result}**"
        )

    @app_commands.command(name="div", description="Divide two numbers")
    @app_commands.describe(
        x="First number",
        y="Second number",
        ndigits="Number of digits to round the result by",
    )
    async def div(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Divide `x` and `y`.
        """

        logging.info(
            "/div x=%s y=%s ndigits=%s invoked by %s", x, y, ndigits, interaction.user
        )

        result = round_on_ndigits(x / y, ndigits)

        await interaction.response.send_message(f"{x} / {y} = **{result}**")

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

        await interaction.response.send_message(f"{x} // {y} = **{x // y}**")

    @app_commands.command(
        name="pow", description="Raise a number to the power of another"
    )
    @app_commands.describe(
        x="Base number",
        y="Exponent number",
        ndigits="Number of digits to round the result by",
    )
    async def pow(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Raise `x` to the power of `y`.
        """

        logging.info(
            "/pow x=%s y=%s ndigits=%s invoked by %s", x, y, ndigits, interaction.user
        )

        result = round_on_ndigits(x**y, ndigits)

        await interaction.response.send_message(f"{x} ^ {y} = **{result}**")

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

        await interaction.response.send_message(f"{x} % {y} = **{x % y}**")

    @app_commands.command(
        name="sqrt", description="Calculate the square root of a number"
    )
    @app_commands.describe(
        x="Number to calculate the square root of",
        ndigits="Number of digits to round the result by",
    )
    async def sqrt(
        self,
        interaction: discord.Interaction,
        x: float,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Calculate the square root of `x`.
        """

        logging.info(
            "/sqrt x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        try:
            result = round_on_ndigits(math.sqrt(x), ndigits)
        except ValueError:  # Negative x
            # Less accurate, but necessary for imaginary
            result = round_on_ndigits(x ** (1 / 2), ndigits)

        await interaction.response.send_message(f"sqrt({x}) = **{result}**")

    @app_commands.command(
        name="cbrt", description="Calculate the cube root of a number"
    )
    @app_commands.describe(
        x="Number to calculate the cube root of",
        ndigits="Number of digits to round the result by",
    )
    async def cbrt(
        self,
        interaction: discord.Interaction,
        x: float,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Calculate the cube root of `x`.
        """

        logging.info(
            "/cbrt x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        result = round_on_ndigits(math.cbrt(x), ndigits)

        await interaction.response.send_message(f"cbrt({x}) = **{result}**")

    @app_commands.command(
        name="nroot", description="Calculate the nth root of a number"
    )
    @app_commands.describe(
        x="Number to calculate the nth root of",
        n="Root number",
        ndigits="Number of digits to round the result by",
    )
    async def nroot(
        self,
        interaction: discord.Interaction,
        x: float,
        n: float,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Calculate the `n`th root of `x`.
        """

        logging.info(
            "/nroot x=%s n=%s ndigits=%s, invoked by %s",
            x,
            n,
            ndigits,
            interaction.user,
        )

        result = round_on_ndigits(x ** (1 / n), ndigits)

        await interaction.response.send_message(f"{n}-root({x}) = **{result}**")

    @app_commands.command(
        name="abs", description="Calculate the absolute value of a number"
    )
    @app_commands.describe(x="Number to calculate the absolute value of")
    async def abs(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the absolute value of `x`.
        """

        logging.info("/abs x=%s invoked by %s", x, interaction.user)

        await interaction.response.send_message(f"abs({x}) = **{abs(x)}**")

    @app_commands.command(name="ceil", description="Calculate the ceiling of a number")
    @app_commands.describe(x="Number to calculate the ceiling of")
    async def ceil(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the ceiling of `x`.
        """

        logging.info("/ceil x=%s invoked by %s", x, interaction.user)

        await interaction.response.send_message(f"ceil({x}) = **{math.ceil(x)}**")

    @app_commands.command(name="floor", description="Calculate the floor of a number")
    @app_commands.describe(x="Number to calculate the floor of")
    async def floor(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the floor of `x`.
        """

        logging.info("/floor x=%s invoked by %s", x, interaction.user)

        await interaction.response.send_message(f"floor({x}) = **{math.floor(x)}**")

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
            f"{x} rounded to {ndigits} decimal places: **{round(x, ndigits)}**)"
        )

    @app_commands.command(name="log", description="Calculate the logarithm of a number")
    @app_commands.describe(
        x="Number to calculate the logarithm of",
        base="Base of the logarithm; if empty, defaults to base e (natural logarithm)",
        ndigits="Number of digits to round the result by",
    )
    async def log(
        self,
        interaction: discord.Interaction,
        x: float,
        base: Optional[float] = None,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Calculate the logarithm base `base` of `x`.
        """

        logging.info(
            "/log x=%s base=%s ndigits=%s invoked by %s",
            x,
            base,
            ndigits,
            interaction.user,
        )

        if base is None:
            result = round_on_ndigits(math.log(x), ndigits)

            await interaction.response.send_message(f"ln({x}) = **{result}**")
            return

        result = round_on_ndigits(math.log(x, base), ndigits)

        await interaction.response.send_message(f"log{base}({x}) = **{result}**")

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

        await interaction.response.send_message(f"gcd({x}, {y}) = **{math.gcd(x, y)}**")

    @app_commands.command(
        name="gcd-bulk",
        description="Calculate the greatest common divisor/denominator "
        + "(GCD) of an arbitrary amount of numbers",
    )
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def gcd_bulk(
        self,
        interaction: discord.Interaction,
        numbers: str,
    ) -> None:
        """
        Calculate the greatest common divisor of an arbitrary amount of numbers.
        """

        logging.info(
            "/gcd-bulk numbers=%s invoked by %s", repr(numbers), interaction.user
        )

        numbers_list = numbers.replace(" ", "").split(
            ","
        )  # Split at commas and remove spaces
        if any(not is_number(num) for num in numbers_list):
            await interaction.response.send_message(
                "Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        floats = (float(num) for num in numbers_list)
        if any(not flt.is_integer() for flt in floats):
            await interaction.response.send_message(
                "Invalid input. Please provide only positive integers separated by commas."
            )
            return

        gcd = math.gcd(*(int(num) for num in numbers_list))

        await interaction.response.send_message(
            f"gcd({", ".join(numbers_list)}) = **{gcd}**"
        )

    @app_commands.command(
        name="lcm",
        description="Calculate the least common multiple (LCM) of two numbers",
    )
    @app_commands.describe(x="First number", y="Second number")
    async def lcm(
        self,
        interaction: discord.Interaction,
        x: int,
        y: int,
    ) -> None:
        """
        Calculate the least common multiple of `x` and `y`.
        """

        logging.info("/lcm x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"lcm({x}, {y}) = **{math.lcm(x, y)}**")

    @app_commands.command(
        name="lcm-bulk",
        description="Calculate the least common multiple (LCM) of an arbitrary amount of numbers",
    )
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def lcm_bulk(
        self,
        interaction: discord.Interaction,
        numbers: str,
    ) -> None:
        """
        Calculate the greatest common divisor of an arbitrary amount of numbers.
        """

        logging.info(
            "/lcm-bulk numbers=%s invoked by %s", repr(numbers), interaction.user
        )

        numbers_list = numbers.replace(" ", "").split(
            ","
        )  # Split at commas and remove spaces
        if any(not is_number(num) for num in numbers_list):
            await interaction.response.send_message(
                "Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        floats = (float(num) for num in numbers_list)
        if any(not flt.is_integer() for flt in floats):
            await interaction.response.send_message(
                "Invalid input. Please provide only positive integers separated by commas."
            )
            return

        lcm = math.lcm(*(int(num) for num in numbers_list))

        await interaction.response.send_message(
            f"lcm({", ".join(numbers_list)}) = **{lcm}**"
        )

    @dist_group.command(
        name="cartesian-2d",
        description="Calculate the Cartesian distance between two points in 2D space",
    )
    @app_commands.describe(
        x1="First x-coordinate",
        y1="First y-coordinate",
        x2="Second x-coordinate",
        y2="Second y-coordinate",
        ndigits="Number of digits to round the result by",
    )
    async def distance_cartesian_2d(  # pylint: disable=too-many-arguments
        self,
        interaction: discord.Interaction,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Calculate the Cartesian distance between two points in 2D.
        """

        logging.info(
            "/distance cartesian-2d x1=%s y1=%s x2=%s y2=%s ndigits=%s invoked by %s",
            x1,
            y1,
            x2,
            y2,
            ndigits,
            interaction.user,
        )

        result = round_on_ndigits(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), ndigits)

        await interaction.response.send_message(
            f"distance(({x1}, {y1}), ({x2}, {y2})) = **{result}**"
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
        ndigits="Number of digits to round the result by",
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
        ndigits: Optional[int] = 10,
    ) -> None:
        """
        Calculate the Cartesian distance between two 3D points.
        """

        logging.info(
            "/distance cartesian-3d x1=%s y1=%s z1=%s x2=%s y2=%s z2=%s ndigits=%s invoked by %s",
            x1,
            y1,
            z1,
            x2,
            y2,
            z2,
            ndigits,
            interaction.user,
        )

        result = round_on_ndigits(
            math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2), ndigits
        )

        await interaction.response.send_message(
            f"distance(({x1}, {y1}, {z1}), ({x2}, {y2}, {z2})) = **{result}**"
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

        await interaction.response.send_message(
            f"factorial({x}) = **{math.factorial(x)}**"
        )


async def setup(bot: commands.Bot):
    """
    Set up the MathCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(MathCog(bot))
