"""Color tools and constants."""

from __future__ import annotations

from io import BytesIO
import re
import secrets

import discord
from PIL import Image

__author__ = "Gavin Borne"
__license__ = "MIT"


_RealNumber = int | float

_RGB_MAX = 255
_RGB_INT_MAX = 16777215
_HEX_LEN = 6

CSS_COLOR_NAME_TO_HEX = {
    "aliceblue": "f0f8ff",
    "antiquewhite": "faebd7",
    "aqua": "00ffff",
    "aquamarine": "7fffd4",
    "azure": "f0ffff",
    "beige": "f5f5dc",
    "bisque": "ffe4c4",
    "black": "000000",
    "blanchedalmond": "ffebcd",
    "blue": "0000ff",
    "blueviolet": "8a2be2",
    "brown": "a52a2a",
    "burlywood": "deb887",
    "cadetblue": "5f9ea0",
    "chartreuse": "7fff00",
    "chocolate": "d2691e",
    "coral": "ff7f50",
    "cornflowerblue": "6495ed",
    "cornsilk": "fff8dc",
    "crimson": "dc143c",
    "cyan": "00ffff",
    "darkblue": "00008b",
    "darkcyan": "008b8b",
    "darkgoldenrod": "b8860b",
    "darkgray": "a9a9a9",
    "darkgrey": "a9a9a9",
    "darkgreen": "006400",
    "darkkhaki": "bdb76b",
    "darkmagenta": "8b008b",
    "darkolivegreen": "556b2f",
    "darkorange": "ff8c00",
    "darkorchid": "9932cc",
    "darkred": "8b0000",
    "darksalmon": "e9967a",
    "darkseagreen": "8fbc8f",
    "darkslateblue": "483d8b",
    "darkslategray": "2f4f4f",
    "darkslategrey": "2f4f4f",
    "darkturquoise": "00ced1",
    "darkviolet": "9400d3",
    "deeppink": "ff1493",
    "deepskyblue": "00bfff",
    "dimgray": "696969",
    "dimgrey": "696969",
    "dodgerblue": "1e90ff",
    "firebrick": "b22222",
    "floralwhite": "fffaf0",
    "forestgreen": "228b22",
    "fuchsia": "ff00ff",
    "gainsboro": "dcdcdc",
    "ghostwhite": "f8f8ff",
    "gold": "ffd700",
    "goldenrod": "daa520",
    "gray": "808080",
    "grey": "808080",
    "green": "008000",
    "greenyellow": "adff2f",
    "honeydew": "f0fff0",
    "hotpink": "ff69b4",
    "indianred": "cd5c5c",
    "indigo": "4b0082",
    "ivory": "fffff0",
    "khaki": "f0e68c",
    "lavender": "e6e6fa",
    "lavenderblush": "fff0f5",
    "lawngreen": "7cfc00",
    "lemonchiffon": "fffacd",
    "lightblue": "add8e6",
    "lightcoral": "f08080",
    "lightcyan": "e0ffff",
    "lightgoldenrodyellow": "fafad2",
    "lightgray": "d3d3d3",
    "lightgrey": "d3d3d3",
    "lightgreen": "90ee90",
    "lightpink": "ffb6c1",
    "lightsalmon": "ffa07a",
    "lightseagreen": "20b2aa",
    "lightskyblue": "87cefa",
    "lightslategray": "778899",
    "lightslategrey": "778899",
    "lightsteelblue": "b0c4de",
    "lightyellow": "ffffe0",
    "lime": "00ff00",
    "limegreen": "32cd32",
    "linen": "faf0e6",
    "magenta": "ff00ff",
    "maroon": "800000",
    "mediumaquamarine": "66cdaa",
    "mediumblue": "0000cd",
    "mediumorchid": "ba55d3",
    "mediumpurple": "9370db",
    "mediumseagreen": "3cb371",
    "mediumslateblue": "7b68ee",
    "mediumspringgreen": "00fa9a",
    "mediumturquoise": "48d1cc",
    "mediumvioletred": "c71585",
    "midnightblue": "191970",
    "mintcream": "f5fffa",
    "mistyrose": "ffe4e1",
    "moccasin": "ffe4b5",
    "navajowhite": "ffdead",
    "navy": "000080",
    "oldlace": "fdf5e6",
    "olive": "808000",
    "olivedrab": "6b8e23",
    "orange": "ffa500",
    "orangered": "ff4500",
    "orchid": "da70d6",
    "palegoldenrod": "eee8aa",
    "palegreen": "98fb98",
    "paleturquoise": "afeeee",
    "palevioletred": "db7093",
    "papayawhip": "ffefd5",
    "peachpuff": "ffdab9",
    "peru": "cd853f",
    "pink": "ffc0cb",
    "plum": "dda0dd",
    "powderblue": "b0e0e6",
    "purple": "800080",
    "rebeccapurple": "663399",
    "red": "ff0000",
    "rosybrown": "bc8f8f",
    "royalblue": "4169e1",
    "saddlebrown": "8b4513",
    "salmon": "fa8072",
    "sandybrown": "f4a460",
    "seagreen": "2e8b57",
    "seashell": "fff5ee",
    "sienna": "a0522d",
    "silver": "c0c0c0",
    "skyblue": "87ceeb",
    "slateblue": "6a5acd",
    "slategray": "708090",
    "slategrey": "708090",
    "snow": "fffafa",
    "springgreen": "00ff7f",
    "steelblue": "4682b4",
    "tan": "d2b48c",
    "teal": "008080",
    "thistle": "d8bfd8",
    "tomato": "ff6347",
    "turquoise": "40e0d0",
    "violet": "ee82ee",
    "wheat": "f5deb3",
    "white": "ffffff",
    "whitesmoke": "f5f5f5",
    "yellow": "ffff00",
    "yellowgreen": "9acd32",
}

_CSS_REDS_NAMES = {
    "crimson",
    "darkred",
    "firebrick",
    "indianred",
    "maroon",
    "red",
    "tomato",
}

_CSS_PINKS_NAMES = {
    "deeppink",
    "hotpink",
    "lightpink",
    "pink",
    "palevioletred",
    "mediumvioletred",
    "mistyrose",
    "lavenderblush",
}

_CSS_ORANGES_NAMES = {
    "coral",
    "chocolate",
    "darkorange",
    "lightsalmon",
    "orange",
    "orangered",
    "peachpuff",
    "sandybrown",
    "salmon",
}

_CSS_YELLOWS_NAMES = {
    "gold",
    "goldenrod",
    "darkgoldenrod",
    "khaki",
    "darkkhaki",
    "lemonchiffon",
    "lightyellow",
    "palegoldenrod",
    "yellow",
    "wheat",
    "cornsilk",
}

_CSS_PURPLES_NAMES = {
    "blueviolet",
    "darkmagenta",
    "darkorchid",
    "darkviolet",
    "fuchsia",
    "indigo",
    "magenta",
    "mediumorchid",
    "mediumpurple",
    "orchid",
    "plum",
    "purple",
    "rebeccapurple",
    "thistle",
    "violet",
    "lavender",
}

_CSS_GREENS_NAMES = {
    "chartreuse",
    "darkgreen",
    "darkolivegreen",
    "darkseagreen",
    "forestgreen",
    "green",
    "greenyellow",
    "honeydew",
    "lawngreen",
    "lightgreen",
    "lime",
    "limegreen",
    "mediumaquamarine",
    "mediumseagreen",
    "mediumspringgreen",
    "olivedrab",
    "palegreen",
    "seagreen",
    "springgreen",
    "yellowgreen",
    "olive",
}

_CSS_BLUES_NAMES = {
    "aliceblue",
    "aqua",
    "aquamarine",
    "azure",
    "blue",
    "cadetblue",
    "cornflowerblue",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkslateblue",
    "darkturquoise",
    "deepskyblue",
    "dodgerblue",
    "lightblue",
    "lightcyan",
    "lightskyblue",
    "lightseagreen",
    "lightsteelblue",
    "mediumblue",
    "mediumslateblue",
    "mediumturquoise",
    "midnightblue",
    "navy",
    "powderblue",
    "royalblue",
    "skyblue",
    "slateblue",
    "steelblue",
    "teal",
    "turquoise",
    "paleturquoise",
}

_CSS_BROWNS_NAMES = {
    "antiquewhite",
    "beige",
    "bisque",
    "blanchedalmond",
    "brown",
    "burlywood",
    "chocolate",
    "darkgoldenrod",
    "linen",
    "moccasin",
    "navajowhite",
    "oldlace",
    "papayawhip",
    "peachpuff",
    "peru",
    "rosybrown",
    "saddlebrown",
    "sienna",
    "tan",
    "wheat",
}

_CSS_WHITES_NAMES = {
    "white",
    "whitesmoke",
    "snow",
    "seashell",
    "ivory",
    "honeydew",
    "mintcream",
    "ghostwhite",
    "floralwhite",
}

_CSS_GRAYS_NAMES = {
    "black",
    "darkgray",
    "darkgrey",
    "dimgray",
    "dimgrey",
    "gainsboro",
    "gray",
    "grey",
    "lightgray",
    "lightgrey",
    "silver",
    "darkslategray",
    "darkslategrey",
    "lightslategray",
    "lightslategrey",
    "slategray",
    "slategrey",
}


def _group_map(names: set[str]) -> dict[str, str]:
    return {name: CSS_COLOR_NAME_TO_HEX[name] for name in names}


CSS_REDS = _group_map(_CSS_REDS_NAMES)
CSS_PINKS = _group_map(_CSS_PINKS_NAMES)
CSS_ORANGES = _group_map(_CSS_ORANGES_NAMES)
CSS_YELLOWS = _group_map(_CSS_YELLOWS_NAMES)
CSS_PURPLES = _group_map(_CSS_PURPLES_NAMES)
CSS_GREENS = _group_map(_CSS_GREENS_NAMES)
CSS_BLUES = _group_map(_CSS_BLUES_NAMES)
CSS_BROWNS = _group_map(_CSS_BROWNS_NAMES)
CSS_WHITES = _group_map(_CSS_WHITES_NAMES)
CSS_GRAYS = _group_map(_CSS_GRAYS_NAMES)

# use reversed to erase dupes, leaving first instance as canonical
HEX_TO_CSS_NAME = {hex6: name for name, hex6 in reversed(CSS_COLOR_NAME_TO_HEX.items())}
"""A map of hex colors mapped to CSS names."""


def _clamp(
    t: _RealNumber,
    /,
    minimum: _RealNumber = float("-inf"),
    maximum: _RealNumber = float("inf"),
) -> _RealNumber:
    if minimum > maximum:
        raise ValueError(
            "'minimum' value passed to clamp cannot be greater than 'maximum' value"
        )

    return min(maximum, max(minimum, t))


def _rem_euclid(lhs: _RealNumber, rhs: _RealNumber) -> _RealNumber:
    abs_rhs = abs(rhs)
    return lhs - abs_rhs * (lhs // abs_rhs)


class ColorParseError(ValueError):
    """Raised when parsing a color fails."""

    def __init__(self, message: str | None = None) -> None:
        """Raise when parsing a color fails.

        Args:
            message (str | None, optional): The error message. Defaults to None.
        """
        super().__init__(message or "Color value out of range")


class Color3:
    """A class representing a 3-value sRGB color."""

    def __init__(self, r: int, g: int, b: int, /) -> None:
        """Create a new sRGB color.

        Args:
            r (int): The red component.
            g (int): The green component.
            b (int): The blue component.

        Raises:
            ColorParseError: If any of the RGB components are out of the valid range.
        """
        if any(x < 0 or x > _RGB_MAX for x in (r, g, b)):
            raise ColorParseError("RGB value out of valid range (0-255)")

        self.__r = r
        self.__g = g
        self.__b = b

    def invert(self, /) -> Color3:
        """Invert this color.

        Returns:
            Color3: The inverted color.
        """
        return Color3(
            abs(_RGB_MAX - self.__r), abs(_RGB_MAX - self.__g), abs(_RGB_MAX - self.__b)
        )

    def lerp(self, other: Color3, t: float, /) -> Color3:
        """Linear interpolation between two sRGB colors.

        Args:
            other (Color3): The color to lerp to.
            t (float): The interpolation value.

        Returns:
            Color3: The interpolated color.
        """

        def lerp8(a: int, b: int) -> int:
            return int(_clamp(round(a + (b - a) * t), 0.0, 255.0))

        t = _clamp(t)
        other_r, other_g, other_b = other.as_rgb()
        return Color3(
            lerp8(self.__r, other_r),
            lerp8(self.__g, other_g),
            lerp8(self.__b, other_b),
        )

    def relative_luminance(self) -> float:
        """Get the WCAG WG relative luminance of this color.

        Source: https://www.w3.org/WAI/GL/wiki/Relative_luminance

        Returns:
            float: The relative luminance.
        """
        r, g, b = self.__as_linear()
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def lighten(self, percent: float, /) -> Color3:
        """Lighten a color.

        Args:
            percent (float): The percentage to lighten by.

        Returns:
            Color3: The lightened color.
        """
        return self.lerp(Color3(255, 255, 255), _clamp(percent, 0.0, 100.0) / 100.0)

    def darken(self, percent: float, /) -> Color3:
        """Darken a color.

        Args:
            percent (float): The percentage to darken by.

        Returns:
            Color3: The darkened color.
        """
        return self.lerp(Color3(0, 0, 0), _clamp(percent, 0.0, 100.0) / 100.0)

    @classmethod
    def random(cls, /) -> Color3:
        """Create a Color3 with a random value.

        Returns:
            Color3: The new color.
        """
        return Color3(
            secrets.randbelow(_RGB_MAX + 1),
            secrets.randbelow(_RGB_MAX + 1),
            secrets.randbelow(_RGB_MAX + 1),
        )

    @classmethod
    def from_discord_color(cls, color: discord.Color, /) -> Color3:
        """Create a Color3 from a discord.py Color.

        Args:
            color (discord.Color): The discord.py Color.

        Returns:
            Color3: The new color.
        """
        return Color3(*color.to_rgb())

    @classmethod
    def from_css_name(cls, name: str, /) -> Color3:
        """Create a Color3 from a CSS color name.

        Args:
            name (str): The CSS color name.

        Returns:
            Color3: The new color.

        Raises:
            ValueError: If an invalid color name is given.
        """
        if name.strip().lower() not in CSS_COLOR_NAME_TO_HEX:
            raise ValueError("Invalid color name")
        return Color3.from_hex6(CSS_COLOR_NAME_TO_HEX[name])

    @classmethod
    def from_hex6(cls, hex6: str, /) -> Color3:
        """Create a Color3 from a 6-digit hex color string.

        Args:
            hex6 (str): The hex string.

        Returns:
            Color3: The new color.
        """
        if hex6.startswith("#"):
            hex6 = hex6[1:]

        if len(hex6) != _HEX_LEN:
            raise ColorParseError(f"Invalid hex6 length ({len(hex6)} != {_HEX_LEN})")

        rgb = tuple(int(hex6[i : i + 2], 16) for i in (0, 2, 4))
        return Color3(*rgb)

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float, /) -> Color3:  # noqa: E741 (ambiguous name)
        """Create a Color3 from an HSL color.

        Args:
            h (float): The hue component (in degrees).
            s (float): The saturation component (0.0-1.0).
            l (float): The lightness component (0.0-1.0).

        Returns:
            Color3: The new color.
        """
        # solution from https://www.rapidtables.com/convert/color/hsl-to-rgb.html
        h, s, l = _rem_euclid(h, 360.0), _clamp(s), _clamp(l)  # noqa: E741 (ambiguous name)

        c = abs(1.0 - (2.0 * l - 1.0)) * s
        x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
        m = l - c / 2.0

        # for ruff's magic value complaints:
        deg_60 = 60.0
        deg_120 = 120.0
        deg_180 = 180.0
        deg_240 = 240.0
        deg_300 = 300.0

        if 0.0 <= h < deg_60:
            rp, gp, bp = c, x, 0.0
        elif deg_60 <= h <= deg_120:
            rp, gp, bp = x, c, 0.0
        elif deg_120 <= h < deg_180:
            rp, gp, bp = 0.0, c, x
        elif deg_180 <= h < deg_240:
            rp, gp, bp = 0.0, x, c
        elif deg_240 <= h < deg_300:
            rp, gp, bp = x, 0.0, c
        else:  # 300.0 <= h < 360.0
            rp, gp, bp = c, 0.0, x

        return Color3(
            round((rp + m) * _RGB_MAX),
            round((gp + m) * _RGB_MAX),
            round((bp + m) * _RGB_MAX),
        )

    @classmethod
    def from_int(cls, integer: int, /) -> Color3:
        """Create a Color3 from an integer.

        Args:
            integer (int): The integer (0xRRGGBB format).

        Returns:
            Color3: The new color.

        Raises:
            ValueError: If the provided int is outside the valid range for RGB colors.
        """
        if integer < 0:
            raise ValueError("RGB int cannot be less than 0")
        if integer > _RGB_INT_MAX:
            raise ValueError(f"RGB int cannot be greater than {_RGB_INT_MAX}")

        return Color3((integer >> 16) & 0xFF, (integer >> 8) & 0xFF, integer & 0xFF)

    def as_discord_color(self) -> discord.Color:
        """Get this color as a discord.py Color.

        Returns:
            discord.Color: The Discord Color.
        """
        return discord.Color.from_rgb(self.__r, self.__g, self.__b)

    def as_css_color(self) -> str | None:
        """Get this color as a CSS color name.

        Returns:
            str | None: The CSS color name matching this color, if it exists.
                None otherwise.
        """
        return HEX_TO_CSS_NAME[self.as_hex6()]

    def as_rgb(self) -> tuple[int, int, int]:
        """Get this color as an RGB tuple.

        Returns:
            tuple[int, int, int]: The RGB tuple.
        """
        return self.__r, self.__g, self.__b

    def as_hex6(self, *, hashtag: bool = False) -> str:
        """Get this color as a 6-digit hex string.

        Args:
            hashtag (bool, optional): Whether to include the hashtag with the string.
                Defaults to False.

        Returns:
            str: The 6-digit hex string.
        """
        return (
            "#" if hashtag else ""
        ) + f"{self.__r:02x}{self.__g:02x}{self.__b:02x}".lower()

    def as_hsl(self) -> tuple[float, float, float]:
        """Get this color as an HSL tuple.

        Returns:
            tuple[float, float, float]: The HSL tuple.
        """
        # solution from https://www.rapidtables.com/convert/color/rgb-to-hsl.html
        rp, gp, bp = (
            float(self.__r) / 255.0,
            float(self.__g) / 255.0,
            float(self.__b) / 255.0,
        )

        c_max = max((rp, gp, bp))
        c_min = min((rp, gp, bp))

        delta = c_max - c_min
        # prevent tiny negative zero from noise
        tiny = 1e-8
        if abs(delta) < tiny:
            delta = 0.0

        if delta == 0.0:
            h = 0.0
        elif rp == c_max:
            h = 60.0 * _rem_euclid((gp - bp) / delta, 6.0)
        elif gp == c_max:
            h = 60.0 * ((bp - rp) / delta + 2.0)
        else:  # bp == c_max
            h = 60.0 * ((rp - gp) / delta + 4.0)

        l = (c_max - c_min) / 2.0  # noqa: E741 (ambiguous name)
        s = 0.0 if delta == 0.0 else delta / (1.0 - abs(2.0 * l - 1.0))

        return h, s, l

    def as_int(self) -> int:
        """Get this color as an int.

        Returns:
            int: An int representation of this color (0xRRGGBB format).
        """
        return (self.__r << 16) | (self.__g << 8) | self.__b

    def __repr__(self) -> str:
        """Get a representation of this color.

        Returns:
            str: The representation of this color.
        """
        return f"Color3({self.__r}, {self.__g}, {self.__b})"

    def __eq__(self, other: object) -> bool:
        """Check if this color is equal to another object.

        Args:
            other (object): The other object to compare with.

        Returns:
            bool: True if the other object is a Color3 with the same r, g, and b values.
                False otherwise.
        """
        return (
            isinstance(other, Color3)
            and self.__r == other.__r
            and self.__g == other.__g
            and self.__b == other.__b
        )

    def __hash__(self) -> int:
        """Generate a hash code for this Color3.

        Returns:
            int: The hash.
        """
        return self.as_int()

    @staticmethod
    def __decode_srgb(srgb: int, /) -> float:
        srgb_f = float(srgb) / 255.0
        c1 = 0.04045
        return srgb_f / 12.92 if srgb_f <= c1 else pow((srgb_f + 0.055) / 1.055, 2.4)

    def __as_linear(self) -> tuple[float, float, float]:
        return (
            self.__decode_srgb(self.__r),
            self.__decode_srgb(self.__g),
            self.__decode_srgb(self.__b),
        )


def validate_rgb(r: int, g: int, b: int, /) -> bool:
    """Determine if the given RGB color is valid.

    Args:
        r (int): The red component.
        g (int): The green component.
        b (int): The blue component.

    Returns:
        bool: Whether the RGB color is valid.
    """
    return all(0 <= v <= _RGB_MAX for v in (r, g, b))


def validate_hex(hex6: str, /) -> bool:
    """Determine if the given 6-digit hex value is valid.

    Args:
        hex6 (str): The hex value to validate.

    Returns:
        bool: Whether the hex is valid.
    """
    return bool(re.match(r"^[A-Fa-f0-9]{6}$", hex6.lstrip("#")))


def generate_color_image(
    color: Color3, /, *, size: tuple[int, int] = (100, 100)
) -> BytesIO:
    """Generate a solid color image from the given color.

    Args:
        color (Color3): The color.
        size (tuple[int, int]): The size of the image (width by height).
            Defaults to (100, 100).

    Returns:
        BytesIO: The bytes of the generated image.
    """
    img = Image.new("RGB", size, color.as_rgb())
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr
