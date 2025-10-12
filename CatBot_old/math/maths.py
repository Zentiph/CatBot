"""
maths.py
Code for mathematical operations/functions to be used for CatBot's math-related commands.
"""

import cmath
import logging
import math

import discord
from discord import app_commands
from discord.ext import commands

from ..CatBot_utils import emojis
from .math_utils import (
    create_sequence_string,
    generate_math_embed_with_icon,
    generate_ordinal_string,
    is_number,
    round_on_ndigits,
    simplify_number_type,
)


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
    @app_commands.describe(
        x="First number",
        y="Second number",
        ndigits="Number of digits to round the result by",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
        ndigits: int = 10,
    ) -> None:
        """
        Add `x` and `y`.
        """

        logging.info(
            "/math add x=%s y=%s ndigits=%s invoked by %s",
            x,
            y,
            ndigits,
            interaction.user,
        )

        x = simplify_number_type(x)
        y = simplify_number_type(y)

        result = simplify_number_type(round_on_ndigits(x + y, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {x} + {y}", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

    @math_group.command(name="sum", description="Sum up an arbitrary amount of numbers")
    @app_commands.describe(
        numbers="An arbitrary amount of numbers separated by commas",
        ndigits="Number of digits to round the result by",
    )
    async def sum(
        self,
        interaction: discord.Interaction,
        numbers: str,
        ndigits: int = 10,
    ) -> None:
        """
        Sum up the provided numbers.
        """

        logging.info(
            "/math sum numbers=%s ndigits=%s invoked by %s",
            repr(numbers),
            ndigits,
            interaction.user,
        )

        await interaction.response.defer(thinking=True)

        numbers_list = numbers.replace(" ", "").split(
            ","
        )  # Split at commas and remove spaces
        if any(not is_number(num) for num in numbers_list):
            await interaction.response.send_message(
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        sequence = create_sequence_string(numbers_list, "+")
        total = sum(float(num) for num in numbers_list)
        result = simplify_number_type(round_on_ndigits(total, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {sequence}", result_value=result
        )

        await interaction.followup.send(embed=embed, file=icon)

    @math_group.command(name="sub", description="Subtract two numbers")
    @app_commands.describe(
        x="First number",
        y="Second number",
        ndigits="Number of digits to round the result by",
    )
    async def sub(
        self,
        interaction: discord.Interaction,
        x: float,
        y: float,
        ndigits: int = 10,
    ) -> None:
        """
        Subtract `x` and `y`.
        """

        logging.info(
            "/math sub x=%s y=%s ndigits=%s invoked by %s",
            x,
            y,
            ndigits,
            interaction.user,
        )

        x = simplify_number_type(x)
        y = simplify_number_type(y)

        result = simplify_number_type(round_on_ndigits(x - y, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"Result of {x} - {y}", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
        ndigits: int = 10,
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

        x = simplify_number_type(x)
        y = simplify_number_type(y)

        result = simplify_number_type(round_on_ndigits(x * y, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {x} * {y}", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
        ndigits: int = 10,
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

        await interaction.response.defer(thinking=True)

        numbers_list = numbers.replace(" ", "").split(
            ","
        )  # Split at commas and remove spaces
        if any(not is_number(num) for num in numbers_list):
            await interaction.response.send_message(
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        sequence = create_sequence_string(numbers_list, "*")
        total = math.prod(float(num) for num in numbers_list)
        result = simplify_number_type(round_on_ndigits(total, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {sequence}", result_value=result
        )

        await interaction.followup.send(embed=embed, file=icon)

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
        ndigits: int = 10,
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

        x = simplify_number_type(x)
        y = simplify_number_type(y)

        result = simplify_number_type(round_on_ndigits(x / y, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {x} * {y}", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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

        x = simplify_number_type(x)
        y = simplify_number_type(y)

        result = x // y

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of floor({x} / {y})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
        ndigits: int = 10,
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

        x = simplify_number_type(x)
        y = simplify_number_type(y)

        result = simplify_number_type(round_on_ndigits(x**y, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {x} ^ {y}", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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

        x = simplify_number_type(x)
        y = simplify_number_type(y)

        result = x % y

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {x} mod {y}", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
        ndigits: int = 10,
    ) -> None:
        """
        Calculate the square root of `x`.
        """

        logging.info(
            "/math sqrt x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        x = simplify_number_type(x)

        if x >= 0.0:
            result = simplify_number_type(round_on_ndigits(math.sqrt(x), ndigits))
        else:  # Negative x doesn't work for math.sqrt
            result = simplify_number_type(round_on_ndigits(x ** (1 / 2), ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of sqrt({x})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

    @math_group.command(name="cbrt", description="Calculate the cube root of a number")
    @app_commands.describe(
        x="Number to calculate the cube root of",
        ndigits="Number of digits to round the result by",
    )
    async def cbrt(
        self,
        interaction: discord.Interaction,
        x: float,
        ndigits: int = 10,
    ) -> None:
        """
        Calculate the cube root of `x`.
        """

        logging.info(
            "/math cbrt x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        x = simplify_number_type(x)

        result = simplify_number_type(round_on_ndigits(math.cbrt(x), ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of cbrt({x})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
        ndigits: int = 10,
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

        x = simplify_number_type(x)
        n = simplify_number_type(n)

        if n == 0:
            await interaction.response.send_message(
                "The root degree (n) must be non-zero.", ephemeral=True
            )
            return

        # Negative base, even root; complex result
        if x < 0.0 and n % 2 == 0:
            base_result = cmath.exp(cmath.log(x) / n)
        # Negative base, odd root; real result
        elif x < 0.0:
            base_result = -abs(x) ** (1 / n)
        else:
            base_result = x ** (1 / n)

        result = simplify_number_type(round_on_ndigits(base_result, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of {generate_ordinal_string(n)}-root({x})",
            result_value=result,
        )

        await interaction.response.send_message(embed=embed, file=icon)

    @math_group.command(
        name="abs", description="Calculate the absolute value of a number"
    )
    @app_commands.describe(x="Number to calculate the absolute value of")
    async def abs(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the absolute value of `x`.
        """

        logging.info("/math abs x=%s invoked by %s", x, interaction.user)

        x = simplify_number_type(x)

        result = abs(x)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of |{x}|", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

    @math_group.command(name="ceil", description="Calculate the ceiling of a number")
    @app_commands.describe(x="Number to calculate the ceiling of")
    async def ceil(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the ceiling of `x`.
        """

        logging.info("/math ceil x=%s invoked by %s", x, interaction.user)

        x = simplify_number_type(x)

        result = math.ceil(x)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of ceil({x})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

    @math_group.command(name="floor", description="Calculate the floor of a number")
    @app_commands.describe(x="Number to calculate the floor of")
    async def floor(self, interaction: discord.Interaction, x: float) -> None:
        """
        Calculate the floor of `x`.
        """

        logging.info("/math floor x=%s invoked by %s", x, interaction.user)

        x = simplify_number_type(x)

        result = math.floor(x)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of floor({x})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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

        x = simplify_number_type(x)

        result = simplify_number_type(round_on_ndigits(x, ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} {x} Rounded to {ndigits} Decimal Places",
            result_value=result,
        )

        await interaction.response.send_message(embed=embed, file=icon)

    @math_group.command(name="log", description="Calculate the logarithm of a number")
    @app_commands.describe(
        x="Number to calculate the logarithm of",
        base="Base of the logarithm",
        ndigits="Number of digits to round the result by",
    )
    async def log(
        self,
        interaction: discord.Interaction,
        x: float,
        base: float = 10.0,
        ndigits: int = 10,
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

        x = simplify_number_type(x)
        base = simplify_number_type(base)

        result = round_on_ndigits(math.log(x, base), ndigits)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of log{base}({x})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

    @math_group.command(
        name="ln", description="Calculate the natural logarithm (base e) of a number"
    )
    @app_commands.describe(
        x="Number to calculate the natural logarithm of",
        ndigits="Number of digits to round the result by",
    )
    async def ln(
        self, interaction: discord.Interaction, x: float, ndigits: int = 10
    ) -> None:
        """
        Calculate the natural logarithm of `x`.
        """

        logging.info(
            "/math ln x=%s ndigits=%s invoked by %s", x, ndigits, interaction.user
        )

        x = simplify_number_type(x)

        result = simplify_number_type(round_on_ndigits(math.log(x), ndigits))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of ln({x})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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

        result = math.gcd(x, y)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of gcd({x}, {y})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        floats = (float(num) for num in numbers_list)
        if any(not flt.is_integer() for flt in floats):
            await interaction.response.send_message(
                f"{emojis.X} Invalid input. Please provide only positive integers separated by commas."
            )
            return

        sequence = create_sequence_string(numbers_list, ", ")
        result = math.gcd(*(int(num) for num in numbers_list))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of gcd({sequence})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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

        result = math.lcm(x, y)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of lcm({x}, {y})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
                f"{emojis.X} Invalid input. Please provide only numbers separated by commas.",
                ephemeral=True,
            )
            return

        floats = (float(num) for num in numbers_list)
        if any(not flt.is_integer() for flt in floats):
            await interaction.response.send_message(
                f"{emojis.X} Invalid input. Please provide only positive integers separated by commas."
            )
            return

        sequence = create_sequence_string(numbers_list, ", ")
        result = math.lcm(*(int(num) for num in numbers_list))

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of lcm({sequence})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
        ndigits: int = 10,
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

        x1 = simplify_number_type(x1)
        y1 = simplify_number_type(y1)
        x2 = simplify_number_type(x2)
        y2 = simplify_number_type(y2)

        result = round_on_ndigits(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), ndigits)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of distance(({x1}, {y1}), ({x2}, {y2}))",
            result_value=result,
        )

        await interaction.response.send_message(embed=embed, file=icon)

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
        ndigits: int = 10,
    ) -> None:
        """
        Calculate the Cartesian distance between two 3D points.
        """

        logging.info(
            "/math distance cartesian-3d "
            + "x1=%s y1=%s z1=%s x2=%s y2=%s z2=%s ndigits=%s invoked by %s",
            x1,
            y1,
            z1,
            x2,
            y2,
            z2,
            ndigits,
            interaction.user,
        )

        x1 = simplify_number_type(x1)
        y1 = simplify_number_type(y1)
        z1 = simplify_number_type(z1)
        x2 = simplify_number_type(x2)
        y2 = simplify_number_type(y2)
        z2 = simplify_number_type(z2)

        result = round_on_ndigits(
            math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2), ndigits
        )

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of distance(({x1}, {y1}, {z1}), ({x2}, {y2}, {z2}))",
            result_value=result,
        )

        await interaction.response.send_message(embed=embed, file=icon)

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

        result = math.factorial(x)

        embed, icon = generate_math_embed_with_icon(
            embed_title=f"{emojis.MATH} Result of factorial({x})", result_value=result
        )

        await interaction.response.send_message(embed=embed, file=icon)


async def setup(bot: commands.Bot):
    """
    Set up the MathCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(MathCog(bot))
