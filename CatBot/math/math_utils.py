"""
mathutils.py
Utils for the math module.
"""

from re import match as re_match
from typing import Any, List, Optional, Tuple, Union, overload

from discord import File, Embed

from ..internal_utils import generate_authored_embed_with_icon


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


@overload
def simplify_number_type(x: int, /) -> int: ...
@overload
def simplify_number_type(x: float, /) -> Union[int, float]: ...
@overload
def simplify_number_type(x: complex, /) -> Union[int, float, complex]: ...
def simplify_number_type(
    x: Union[int, float, complex], /
) -> Union[int, float, complex]:
    """
    Simply `x` if possible to the least complex number type.
    Examples below.

    :param x: Number to simplify
    :type x: Union[int, float, complex]
    :return: Simplified number
    :rtype: Union[int, float, complex]

    ```
    >>> simplify_number_type(3)
    3
    >>> simplify_number_type(3.0)
    3
    >>> simplify_number_type(3.0 + 0.0j)
    3
    ```
    """

    if isinstance(x, complex):
        real, imag = x.real, x.imag

        if real.is_integer():
            real = int(real)

        if imag == 0.0:
            return real
        if imag.is_integer():
            imag = int(imag)

        return complex(real, imag)

    if isinstance(x, float):
        if x.is_integer():
            return int(x)
        return x

    # If int, just return it; it cannot be simplified
    return x


def complex_to_string(x: complex, /) -> str:
    """
    Convert `x` to a string representation to be used in embeds.

    :param x: Number to convert
    :type x: complex
    :return: String representation of `x`
    :rtype: str
    """

    return f"{simplify_number_type(x.real)} + {simplify_number_type(x.imag)}i"


def create_sequence_string(
    sequence: List[str], operator: str, /, *, cutoff_number=10
) -> str:
    """
    Simplify the sequence string (e.g. "1,2,-3,4").

    :param sequence: Sequence string to simplify
    :type sequence: List[str]
    :param operator: The operator to place in between numbers (e.g. "+", "*")
    :type operator: str
    :param cutoff_number: Number to cut the string off at to
    prevent an overly long string, defaults to 10
    :type cutoff_number: int, optional
    :return: Simplified string
    :rtype: str
    """

    numbers = tuple(float(num) for num in sequence)
    sequence_str = ""

    for i, num in enumerate(numbers):
        simplified_num = simplify_number_type(num)

        if i == 0:  # First number
            sequence_str += str(simplified_num)
            continue

        # Check if next operator should be plus or minus (if operator == "+")
        if operator == "+":
            if simplified_num < 0:  # type: ignore
                sequence_str += " - " + str(-simplified_num)
            else:
                sequence_str += " + " + str(simplified_num)
        elif operator == "*":
            sequence_str += f" * {str(simplified_num)}"
        else:
            sequence_str += f"{operator}{str(simplified_num)}"

        if i == cutoff_number:  # Cutoff point
            if operator in ("+", "*"):
                sequence_str += f" {operator} ..."
            else:
                sequence_str += f"{operator}..."
            break

    return sequence_str


def generate_math_embed_with_icon(
    *,
    embed_title: Optional[Any] = None,
    embed_description: Optional[Any] = "Here's the result of your calculation.",
    result_title: str = "Result",
    result_value: Any,
) -> Tuple[Embed, File]:
    """
    Generate an authored embed and the file icon required.
    Simplified version of the base function for the math module's embeds.

    :param embed_title: Title of the embed, defaults to None
    :type embed_title: Any | None
    :param embed_description: Description of the embed,
    defaults to "Here's the result of your calculation."
    :type embed_description: Any | None, optional
    :param result_title: The title of the result embed field, defaults to "Result"
    :type result_title: str
    :param result_value: The value of the result to display
    :type result_value: Any
    :return: The embed and icon file in a tuple
    :rtype: Tuple[Embed, File]
    """

    embed, icon = generate_authored_embed_with_icon(
        embed_title=embed_title, embed_description=embed_description
    )
    embed.add_field(name=result_title, value=result_value)

    return embed, icon


def generate_ordinal_string(number: Union[int, float]) -> str:
    """
    Convert a number into its ordinal string.
    See below for examples.

    :param number: Number
    :type number: int | float
    :return: Ordinal string
    :rtype: str

    ```
    >>> generate_ordinal_string(1)
    1st
    >>> generate_ordinal_string(2)
    2nd
    >>> generate_ordinal_string(3)
    3rd
    >>> generate_ordinal_string(4)
    4th
    >>> generate_ordinal_string(1998)
    1998th
    ```
    """

    reference_digit = str(number)[-1]

    if reference_digit == 1:
        return f"{number}st"
    if reference_digit == 2:
        return f"{number}nd"
    if reference_digit == 3:
        return f"{number}rd"
    return f"{number}th"
