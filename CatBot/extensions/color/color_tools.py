"""
Color tools and constants.
"""

import random
import re

__author__ = "Gavin Borne"
__license__ = "MIT"

REDS = {
    "indian red": "cd5c5c",
    "light coral": "f08080",
    "salmon": "fa9072",
    "dark salmon": "e9967a",
    "crimson": "dc143c",
    "red": "ff0000",
    "fire brick": "b22222",
    "dark red": "8b0000",
}
"""A map of red CSS color names to their values."""

PINKS = {
    "pink": "ffc0cb",
    "light pink": "ffb6c1",
    "hot pink": "ff69b4",
    "deep pink": "ff1493",
    "medium violet red": "c71585",
    "pale violet red": "db7093",
}
"""A map of pink CSS color names to their values."""


ORANGES = {
    "light salmon": "ffa07a",
    "coral": "ff7f50",
    "tomato": "ff6347",
    "orange red": "ff4500",
    "dark orange": "ff8c00",
    "orange": "ffa500",
}
"""A map of orange CSS color names to their values."""


YELLOWS = {
    "gold": "ffd700",
    "yellow": "ffff00",
    "light yellow": "ffffe0",
    "lemon chiffon": "fffacd",
    "light goldenrod yellow": "fafad2",
    "papaya whip": "ffefd2",
    "moccasin": "ffe4b5",
    "peach puff": "ffdab9",
    "pale goldenrod": "eee8aa",
    "khaki": "f0e68c",
    "dark khaki": "bdb76b",
}
"""A map of yellow CSS color names to their values."""


PURPLES = {
    "lavender": "e6e6fa",
    "thistle": "d8bfd8",
    "plum": "dda0dd",
    "violet": "ee82ee",
    "orchid": "da70d6",
    "magenta": "ff00ff",
    "medium orchid": "ba55d3",
    "medium purple": "9370db",
    "rebecca purple": "663399",
    "blue violet": "8a2be2",
    "dark violet": "9400d3",
    "dark orchid": "9932cc",
    "dark magenta": "8b008b",
    "purple": "800080",
    "indigo": "4b0082",
    "slate blue": "6a5acd",
    "dark slate blue": "483d8b",
}
"""A map of purple CSS color names to their values."""


GREENS = {
    "green yellow": "adff2f",
    "chartreuse": "7fff00",
    "lawn green": "7cfc00",
    "lime": "00ff00",
    "lime green": "32cd32",
    "pale green": "98fb98",
    "light green": "90ee90",
    "medium spring green": "00fa9a",
    "spring green": "00ff7f",
    "medium sea green": "3cb371",
    "sea green": "2e8b57",
    "forest green": "228b22",
    "green": "008000",
    "dark green": "006400",
    "yellow green": "9acd32",
    "olive drab": "6b8e23",
    "olive": "808000",
    "dark olive green": "556b2f",
    "medium aquamarine": "66cdaa",
    "dark sea green": "8fbc8b",
    "light sea green": "20b2aa",
    "dark cyan": "008b8b",
    "teal": "008080",
}
"""A map of green CSS color names to their values."""


BLUES = {
    "cyan": "00ffff",
    "light cyan": "e0ffff",
    "pale turquoise": "afeeee",
    "aquamarine": "7fffd4",
    "turquoise": "40e0d0",
    "medium turquoise": "48d1cc",
    "dark turquoise": "00ced1",
    "cadet blue": "5f9ea0",
    "steel blue": "4682b4",
    "light steel blue": "b0c4de",
    "powder blue": "b0e0e6",
    "light blue": "add8e6",
    "sky blue": "87ceeb",
    "light sky blue": "87cefa",
    "deep sky blue": "00bfff",
    "dodger blue": "1e90ff",
    "cornflower blue": "6495ed",
    "royal blue": "4169e1",
    "blue": "0000ff",
    "medium blue": "0000cd",
    "dark blue": "00008b",
    "navy": "000080",
    "midnight blue": "191970",
}
"""A map of blue CSS color names to their values."""


BROWNS = {
    "cornsilk": "fff8dc",
    "blanched almond": "ffebcd",
    "bisque": "ffe4c4",
    "navajo white": "ffdead",
    "wheat": "f5deb3",
    "burly wood": "deb887",
    "tan": "d2b48c",
    "rosy brown": "bc8f8f",
    "sandy brown": "f4a460",
    "goldenrod": "daa520",
    "dark goldenrod": "b8860b",
    "peru": "cd853f",
    "chocolate": "d2691e",
    "saddle brown": "8b4513",
    "sienna": "a0522d",
    "brown": "a52a2a",
    "maroon": "800000",
}
"""A map of brown CSS color names to their values."""


WHITES = {
    "white": "ffffff",
    "snow": "fffafa",
    "honey dew": "f0fff0",
    "mint cream": "f5fffa",
    "azure": "f0ffff",
    "alice blue": "f0f8ff",
    "ghost white": "f8f8ff",
    "white smoke": "f5f5f5",
    "sea shell": "fff5ee",
    "beige": "f5f5dc",
    "old lace": "fdf5e6",
    "floral white": "fffaf0",
    "ivory": "fffff0",
    "antique white": "faebd7",
    "linen": "faf0e6",
    "lavender blush": "fff0f5",
    "misty rose": "ffe4e1",
}
"""A map of white CSS color names to their values."""


GRAYS = {
    "gainsboro": "dcdcdc",
    "light gray": "d3d3d3",
    "silver": "c0c0c0",
    "dark gray": "a9a9a9",
    "gray": "808080",
    "dim gray": "696969",
    "light slate gray": "778899",
    "slate gray": "708090",
    "dark slate gray": "2f4f4f",
    "black": "000001",  # has to be #000001 since discord reserves #000000 for no color
}
"""A map of gray CSS color names to their values."""


COLORS = {}
"""A map of CSS color names to their values."""
COLORS.update(REDS)
COLORS.update(ORANGES)
COLORS.update(YELLOWS)
COLORS.update(GREENS)
COLORS.update(BLUES)
COLORS.update(PURPLES)
COLORS.update(PINKS)
COLORS.update(BROWNS)
COLORS.update(WHITES)
COLORS.update(GRAYS)


def is_hex_value(hex6: str, /) -> bool:
    """
    Determine if `hex6` is a valid hex value.

    :param hex6: Hex value to check.
    :type hex6: str
    :return: Whether `hex6` is valid.
    :rtype: bool
    """

    return bool(re.match(r"^[A-Fa-f0-9]{6}$", hex6.strip("#")))


def is_rgb_value(value: int, /) -> bool:
    """
    Determine if `value` is a valid RGB value.

    :param value: Value to check.
    :type value: int
    :return: Whether `value` is valid.
    :rtype: bool
    """

    return 0 <= value <= 255


def random_rgb(*, seed: str | None = None) -> tuple[int, int, int]:
    """
    Generate a random RGB value.

    :param seed: Optional seed, defaults to None
    :type seed: str | None, optional
    :return: Random RGB value.
    :rtype: tuple[int, int, int]
    """

    if seed:
        random.seed(seed)
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def invert_rgb(r: int, g: int, b: int, /) -> tuple[int, int, int]:
    """
    Invert `r`, `g`, and `b`.

    :param r: Red value
    :type r: int
    :param g: Blue value
    :type g: int
    :param b: Blue value
    :type b: int
    :return: Inverted RGB
    :rtype: tuple[int, int, int]
    """

    return abs(255 - r), abs(255 - g), abs(255 - b)


def invert_hex(hex6: str, /) -> str:
    """
    Invert the `hex6`.

    :param hex6: Hex value
    :type hex6: str
    :return: Inverted hex value
    :rtype: tuple[int, int, int]
    """

    r, g, b = hex2rgb(hex6)
    ir, ig, ib = invert_rgb(r, g, b)
    return rgb2hex(ir, ig, ib)


def hex2rgb(hex6: str, /) -> tuple[int, int, int]:
    """
    Translate `hex6` into RGB.

    :param hex6: Hex value
    :type hex6: str
    :return: Converted RGB value
    :rtype: tuple[int, int, int]
    """

    hex6 = hex6.strip("#")
    return tuple(int(hex6[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore


def rgb2hex(r: int, g: int, b: int, /) -> str:
    """
    Translate `r`, `g`, and `b` to hex.

    :param r: Red value
    :type r: int
    :param g: Green value
    :type g: int
    :param b: Blue value
    :type b: int
    :return: Converted hex value
    :rtype: str
    """

    return f"{r:02x}{g:02x}{b:02x}".lower()


def random_hex() -> str:
    """
    Generate a random hex value.

    :return: The hex value
    :rtype: str
    """

    r, g, b = random_rgb()
    return rgb2hex(r, g, b)
