"""
maths.py
Code for mathematical operations/functions to be used for CatBot's math-related commands.
"""

import cmath
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

    math_group = app_commands.Group(name="math", description="Math commands")
    dist_group = app_commands.Group(
        name="distance",
        description="Calculate the distance between two points",
        parent=math_group,
    )

    @math_group.command(name="add", description="Add two numbers")
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

        logging.info("/math add x=%s y=%s invoked by %s", x, y, interaction.user)

        await interaction.response.send_message(f"{x} + {y} = **{x + y}**")

    @math_group.command(name="sum", description="Sum up an arbitrary amount of numbers")
    @app_commands.describe(numbers="An arbitrary amount of numbers separated by commas")
    async def sum(
        self,
        interaction: discord.Interaction,
        numbers: str,
    ) -> None:
        """
        Sum up the provided numbers.
        """

        logging.info(
            "/math sum numbers=%s invoked by %s", repr(numbers), interaction.user
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
        total = sum(float(num) for num in numbers_list)

        await interaction.response.send_message(
            f"{" + ".join(numbers_list)} = **{total}**"
        )

    @math_group.command(name="sub", description="Subtract two numbers")
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

        logging.info("/math sub x=%s y=%s invoked by %s", x, y, interaction.user)

        await interaction.response.send_message(f"{x} - {y} = **{x - y}**")

    @math_group.command(name="mul", description="Multiply two numbers")
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
            "/math mul x=%s y=%s ndigits=%s invoked by %s",
            x,
            y,
            ndigits,
            interaction.user,
        )

        result = round_on_ndigits(x + y, ndigits)

        await interaction.response.send_message(f"{x} * {y} = **{result}**")

    @math_group.command(
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
            "/math prod numbers=%s ndigits=%s invoked by %s",
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

    @math_group.command(name="div", description="Divide two numbers")
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
            "/math div x=%s y=%s ndigits=%s invoked by %s",
            x,
            y,
            ndigits,
            interaction.user,
        )

        result = round_on_ndigits(x / y, ndigits)

        await interaction.response.send_message(f"{x} / {y} = **{result}**")

    @math_group.command(
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

        logging.info("/math floordiv x=%s y=%s invoked by %s", x, y, interaction.user)

        await interaction.response.send_message(f"{x} // {y} = **{x // y}**")

    @math_group.command(
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
            "/math pow x=%s y=%s ndigits=%s invoked by %s",
            x,
            y,
            ndigits,
            interaction.user,
        )

        result = round_on_ndigits(x**y, ndigits)

        await interaction.response.send_message(f"{x} ^ {y} = **{result}**")

    @math_group.command(name="mod", description="Calculate the modulus of two numbers")
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

        logging.info("/math mod x=%s y=%s invoked by %s", x, y, interaction.user)

        await interaction.response.send_message(f"{x} % {y} = **{x % y}**")

    @math_group.command(
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
            "/math sqrt x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        if x >= 0.0:
            result = round_on_ndigits(math.sqrt(x), ndigits)
        else:  # Negative x doesn't work for math.sqrt
            result = round_on_ndigits(x ** (1 / 2), ndigits)

        await interaction.response.send_message(f"sqrt({x}) = **{result}**")

    @math_group.command(name="cbrt", description="Calculate the cube root of a number")
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
            "/math cbrt x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        result = round_on_ndigits(math.cbrt(x), ndigits)

        await interaction.response.send_message(f"cbrt({x}) = **{result}**")

    @math_group.command(name="nroot", description="Calculate the nth root of a number")
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
            "/math nroot x=%s n=%s ndigits=%s, invoked by %s",
            x,
            n,
            ndigits,
            interaction.user,
        )

        if n == 0:
            await interaction.response.send_message(
                "The root degree (n) must be non-zero.", ephemeral=True
            )
            return

        # Negative base, even root; complex result
        if x < 0 and n % 2 == 0:
            base_result = cmath.exp(cmath.log(x) / n)
        # Negative base, odd root; real result
        elif x < 0:
            base_result = -abs(x) ** (1 / n)
        else:
            base_result = x ** (1 / n)

        result = round_on_ndigits(base_result, ndigits)

        await interaction.response.send_message(f"{n}-root({x}) = **{result}**")

    @math_group.command(
        name="abs", description="Calculate the absolute value of a number"
    )
    @app_commands.describe(x="Number to calculate the absolute value of")
    async def abs(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the absolute value of `x`.
        """

        logging.info("/math abs x=%s invoked by %s", x, interaction.user)

        await interaction.response.send_message(f"abs({x}) = **{abs(x)}**")

    @math_group.command(name="ceil", description="Calculate the ceiling of a number")
    @app_commands.describe(x="Number to calculate the ceiling of")
    async def ceil(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the ceiling of `x`.
        """

        logging.info("/math ceil x=%s invoked by %s", x, interaction.user)

        await interaction.response.send_message(f"ceil({x}) = **{math.ceil(x)}**")

    @math_group.command(name="floor", description="Calculate the floor of a number")
    @app_commands.describe(x="Number to calculate the floor of")
    async def floor(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the floor of `x`.
        """

        logging.info("/math floor x=%s invoked by %s", x, interaction.user)

        await interaction.response.send_message(f"floor({x}) = **{math.floor(x)}**")

    @math_group.command(
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
            "/math round x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        await interaction.response.send_message(
            f"{x} rounded to {ndigits} decimal places: **{round(x, ndigits)}**)"
        )

    @math_group.command(name="log", description="Calculate the logarithm of a number")
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
            "/math log x=%s base=%s ndigits=%s invoked by %s",
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

    @math_group.command(
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

        logging.info("/math gcd x=%s y=%s invoked by %s", x, y, interaction.user)

        await interaction.response.send_message(f"gcd({x}, {y}) = **{math.gcd(x, y)}**")

    @math_group.command(
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
            "/math gcd-bulk numbers=%s invoked by %s", repr(numbers), interaction.user
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

    @math_group.command(
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

        logging.info("/math lcm x=%s y=%s invoked by %s", x, y, interaction.user)
        await interaction.response.send_message(f"lcm({x}, {y}) = **{math.lcm(x, y)}**")

    @math_group.command(
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
            "/math lcm-bulk numbers=%s invoked by %s", repr(numbers), interaction.user
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
            "/math distance cartesian-2d x1=%s y1=%s x2=%s y2=%s ndigits=%s invoked by %s",
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
            "/math distance cartesian-3d x1=%s y1=%s z1=%s x2=%s y2=%s z2=%s ndigits=%s invoked by %s",
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

    @math_group.command(
        name="factorial", description="Calculate the factorial of a number"
    )
    @app_commands.describe(x="Number to calculate the factorial of")
    async def factorial(self, interaction: discord.Interaction, x: int) -> None:
        """
        Calculate the factorial of a number.
        """

        logging.info("/math factorial x=%s invoked by %s", x, interaction.user)

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
