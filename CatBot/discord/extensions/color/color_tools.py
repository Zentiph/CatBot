"""Color tools and constants."""

from __future__ import annotations

from io import BytesIO
import re
import secrets

import discord
from PIL import Image

__author__ = "Gavin Borne"
__license__ = "MIT"

RealNumber = int | float

RGB_MAX = 255
"""The maximum value of an RGB component."""

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
    "transparent": "00000000",
    "turquoise": "40e0d0",
    "violet": "ee82ee",
    "wheat": "f5deb3",
    "white": "ffffff",
    "whitesmoke": "f5f5f5",
    "yellow": "ffff00",
    "yellowgreen": "9acd32",
}
"""A map of CSS color names to their hex values."""

CSS_REDS = {
    "crimson": CSS_COLOR_NAME_TO_HEX["crimson"],
    "darkred": CSS_COLOR_NAME_TO_HEX["darkred"],
    "firebrick": CSS_COLOR_NAME_TO_HEX["firebrick"],
    "indianred": CSS_COLOR_NAME_TO_HEX["indianred"],
    "maroon": CSS_COLOR_NAME_TO_HEX["maroon"],
    "red": CSS_COLOR_NAME_TO_HEX["red"],
    "tomato": CSS_COLOR_NAME_TO_HEX["tomato"],
}
"""A map of red CSS color names to their hex values."""

CSS_PINKS = {
    "deeppink": CSS_COLOR_NAME_TO_HEX["deeppink"],
    "hotpink": CSS_COLOR_NAME_TO_HEX["hotpink"],
    "lightpink": CSS_COLOR_NAME_TO_HEX["lightpink"],
    "pink": CSS_COLOR_NAME_TO_HEX["pink"],
    "palevioletred": CSS_COLOR_NAME_TO_HEX["palevioletred"],
    "mediumvioletred": CSS_COLOR_NAME_TO_HEX["mediumvioletred"],
    "mistyrose": CSS_COLOR_NAME_TO_HEX["mistyrose"],
    "lavenderblush": CSS_COLOR_NAME_TO_HEX["lavenderblush"],
}
"""A map of pink CSS color names to their hex values."""

CSS_ORANGES = {
    "coral": CSS_COLOR_NAME_TO_HEX["coral"],
    "chocolate": CSS_COLOR_NAME_TO_HEX["chocolate"],
    "darkorange": CSS_COLOR_NAME_TO_HEX["darkorange"],
    "lightsalmon": CSS_COLOR_NAME_TO_HEX["lightsalmon"],
    "orange": CSS_COLOR_NAME_TO_HEX["orange"],
    "orangered": CSS_COLOR_NAME_TO_HEX["orangered"],
    "peachpuff": CSS_COLOR_NAME_TO_HEX["peachpuff"],
    "sandybrown": CSS_COLOR_NAME_TO_HEX["sandybrown"],
    "salmon": CSS_COLOR_NAME_TO_HEX["salmon"],
}
"""A map of orange CSS color names to their hex values."""

CSS_YELLOWS = {
    "gold": CSS_COLOR_NAME_TO_HEX["gold"],
    "goldenrod": CSS_COLOR_NAME_TO_HEX["goldenrod"],
    "darkgoldenrod": CSS_COLOR_NAME_TO_HEX["darkgoldenrod"],
    "khaki": CSS_COLOR_NAME_TO_HEX["khaki"],
    "darkkhaki": CSS_COLOR_NAME_TO_HEX["darkkhaki"],
    "lemonchiffon": CSS_COLOR_NAME_TO_HEX["lemonchiffon"],
    "lightyellow": CSS_COLOR_NAME_TO_HEX["lightyellow"],
    "palegoldenrod": CSS_COLOR_NAME_TO_HEX["palegoldenrod"],
    "yellow": CSS_COLOR_NAME_TO_HEX["yellow"],
    "wheat": CSS_COLOR_NAME_TO_HEX["wheat"],
    "cornsilk": CSS_COLOR_NAME_TO_HEX["cornsilk"],
}
"""A map of yellow CSS color names to their hex values."""

CSS_PURPLES = {
    "blueviolet": CSS_COLOR_NAME_TO_HEX["blueviolet"],
    "darkmagenta": CSS_COLOR_NAME_TO_HEX["darkmagenta"],
    "darkorchid": CSS_COLOR_NAME_TO_HEX["darkorchid"],
    "darkviolet": CSS_COLOR_NAME_TO_HEX["darkviolet"],
    "fuchsia": CSS_COLOR_NAME_TO_HEX["fuchsia"],
    "indigo": CSS_COLOR_NAME_TO_HEX["indigo"],
    "magenta": CSS_COLOR_NAME_TO_HEX["magenta"],
    "mediumorchid": CSS_COLOR_NAME_TO_HEX["mediumorchid"],
    "mediumpurple": CSS_COLOR_NAME_TO_HEX["mediumpurple"],
    "orchid": CSS_COLOR_NAME_TO_HEX["orchid"],
    "plum": CSS_COLOR_NAME_TO_HEX["plum"],
    "purple": CSS_COLOR_NAME_TO_HEX["purple"],
    "rebeccapurple": CSS_COLOR_NAME_TO_HEX["rebeccapurple"],
    "thistle": CSS_COLOR_NAME_TO_HEX["thistle"],
    "violet": CSS_COLOR_NAME_TO_HEX["violet"],
    "lavender": CSS_COLOR_NAME_TO_HEX["lavender"],
}
"""A map of purple CSS color names to their hex values."""

CSS_GREENS = {
    "chartreuse": CSS_COLOR_NAME_TO_HEX["chartreuse"],
    "darkgreen": CSS_COLOR_NAME_TO_HEX["darkgreen"],
    "darkolivegreen": CSS_COLOR_NAME_TO_HEX["darkolivegreen"],
    "darkseagreen": CSS_COLOR_NAME_TO_HEX["darkseagreen"],
    "forestgreen": CSS_COLOR_NAME_TO_HEX["forestgreen"],
    "green": CSS_COLOR_NAME_TO_HEX["green"],
    "greenyellow": CSS_COLOR_NAME_TO_HEX["greenyellow"],
    "honeydew": CSS_COLOR_NAME_TO_HEX["honeydew"],
    "lawngreen": CSS_COLOR_NAME_TO_HEX["lawngreen"],
    "lightgreen": CSS_COLOR_NAME_TO_HEX["lightgreen"],
    "lime": CSS_COLOR_NAME_TO_HEX["lime"],
    "limegreen": CSS_COLOR_NAME_TO_HEX["limegreen"],
    "mediumaquamarine": CSS_COLOR_NAME_TO_HEX["mediumaquamarine"],
    "mediumseagreen": CSS_COLOR_NAME_TO_HEX["mediumseagreen"],
    "mediumspringgreen": CSS_COLOR_NAME_TO_HEX["mediumspringgreen"],
    "olivedrab": CSS_COLOR_NAME_TO_HEX["olivedrab"],
    "palegreen": CSS_COLOR_NAME_TO_HEX["palegreen"],
    "seagreen": CSS_COLOR_NAME_TO_HEX["seagreen"],
    "springgreen": CSS_COLOR_NAME_TO_HEX["springgreen"],
    "yellowgreen": CSS_COLOR_NAME_TO_HEX["yellowgreen"],
    "olive": CSS_COLOR_NAME_TO_HEX["olive"],
}
"""A map of green CSS color names to their hex values."""

CSS_BLUES = {
    "aliceblue": CSS_COLOR_NAME_TO_HEX["aliceblue"],
    "aqua": CSS_COLOR_NAME_TO_HEX["aqua"],
    "aquamarine": CSS_COLOR_NAME_TO_HEX["aquamarine"],
    "azure": CSS_COLOR_NAME_TO_HEX["azure"],
    "blue": CSS_COLOR_NAME_TO_HEX["blue"],
    "cadetblue": CSS_COLOR_NAME_TO_HEX["cadetblue"],
    "cornflowerblue": CSS_COLOR_NAME_TO_HEX["cornflowerblue"],
    "cyan": CSS_COLOR_NAME_TO_HEX["cyan"],
    "darkblue": CSS_COLOR_NAME_TO_HEX["darkblue"],
    "darkcyan": CSS_COLOR_NAME_TO_HEX["darkcyan"],
    "darkslateblue": CSS_COLOR_NAME_TO_HEX["darkslateblue"],
    "darkturquoise": CSS_COLOR_NAME_TO_HEX["darkturquoise"],
    "deepskyblue": CSS_COLOR_NAME_TO_HEX["deepskyblue"],
    "dodgerblue": CSS_COLOR_NAME_TO_HEX["dodgerblue"],
    "lightblue": CSS_COLOR_NAME_TO_HEX["lightblue"],
    "lightcyan": CSS_COLOR_NAME_TO_HEX["lightcyan"],
    "lightskyblue": CSS_COLOR_NAME_TO_HEX["lightskyblue"],
    "lightseagreen": CSS_COLOR_NAME_TO_HEX["lightseagreen"],
    "lightsteelblue": CSS_COLOR_NAME_TO_HEX["lightsteelblue"],
    "mediumblue": CSS_COLOR_NAME_TO_HEX["mediumblue"],
    "mediumslateblue": CSS_COLOR_NAME_TO_HEX["mediumslateblue"],
    "mediumturquoise": CSS_COLOR_NAME_TO_HEX["mediumturquoise"],
    "midnightblue": CSS_COLOR_NAME_TO_HEX["midnightblue"],
    "navy": CSS_COLOR_NAME_TO_HEX["navy"],
    "powderblue": CSS_COLOR_NAME_TO_HEX["powderblue"],
    "royalblue": CSS_COLOR_NAME_TO_HEX["royalblue"],
    "skyblue": CSS_COLOR_NAME_TO_HEX["skyblue"],
    "slateblue": CSS_COLOR_NAME_TO_HEX["slateblue"],
    "steelblue": CSS_COLOR_NAME_TO_HEX["steelblue"],
    "teal": CSS_COLOR_NAME_TO_HEX["teal"],
    "turquoise": CSS_COLOR_NAME_TO_HEX["turquoise"],
    "paleturquoise": CSS_COLOR_NAME_TO_HEX["paleturquoise"],
}
"""A map of blue CSS color names to their hex values."""

CSS_BROWNS = {
    "antiquewhite": CSS_COLOR_NAME_TO_HEX["antiquewhite"],
    "beige": CSS_COLOR_NAME_TO_HEX["beige"],
    "bisque": CSS_COLOR_NAME_TO_HEX["bisque"],
    "blanchedalmond": CSS_COLOR_NAME_TO_HEX["blanchedalmond"],
    "brown": CSS_COLOR_NAME_TO_HEX["brown"],
    "burlywood": CSS_COLOR_NAME_TO_HEX["burlywood"],
    "chocolate": CSS_COLOR_NAME_TO_HEX["chocolate"],
    "darkgoldenrod": CSS_COLOR_NAME_TO_HEX["darkgoldenrod"],
    "linen": CSS_COLOR_NAME_TO_HEX["linen"],
    "moccasin": CSS_COLOR_NAME_TO_HEX["moccasin"],
    "navajowhite": CSS_COLOR_NAME_TO_HEX["navajowhite"],
    "oldlace": CSS_COLOR_NAME_TO_HEX["oldlace"],
    "papayawhip": CSS_COLOR_NAME_TO_HEX["papayawhip"],
    "peachpuff": CSS_COLOR_NAME_TO_HEX["peachpuff"],
    "peru": CSS_COLOR_NAME_TO_HEX["peru"],
    "rosybrown": CSS_COLOR_NAME_TO_HEX["rosybrown"],
    "saddlebrown": CSS_COLOR_NAME_TO_HEX["saddlebrown"],
    "sienna": CSS_COLOR_NAME_TO_HEX["sienna"],
    "tan": CSS_COLOR_NAME_TO_HEX["tan"],
    "wheat": CSS_COLOR_NAME_TO_HEX["wheat"],
}
"""A map of brown CSS color names to their hex values."""

CSS_WHITES = {
    "floralwhite": CSS_COLOR_NAME_TO_HEX["floralwhite"],
    "ghostwhite": CSS_COLOR_NAME_TO_HEX["ghostwhite"],
    "honeydew": CSS_COLOR_NAME_TO_HEX["honeydew"],
    "ivory": CSS_COLOR_NAME_TO_HEX["ivory"],
    "mintcream": CSS_COLOR_NAME_TO_HEX["mintcream"],
    "seashell": CSS_COLOR_NAME_TO_HEX["seashell"],
    "snow": CSS_COLOR_NAME_TO_HEX["snow"],
    "white": CSS_COLOR_NAME_TO_HEX["white"],
    "whitesmoke": CSS_COLOR_NAME_TO_HEX["whitesmoke"],
    "aliceblue": CSS_COLOR_NAME_TO_HEX["aliceblue"],
    "azure": CSS_COLOR_NAME_TO_HEX["azure"],
    "cornsilk": CSS_COLOR_NAME_TO_HEX["cornsilk"],
    "lemonchiffon": CSS_COLOR_NAME_TO_HEX["lemonchiffon"],
    "lightyellow": CSS_COLOR_NAME_TO_HEX["lightyellow"],
    "linen": CSS_COLOR_NAME_TO_HEX["linen"],
    "oldlace": CSS_COLOR_NAME_TO_HEX["oldlace"],
    "papayawhip": CSS_COLOR_NAME_TO_HEX["papayawhip"],
}
"""A map of white CSS color names to their hex values."""

CSS_GRAYS = {
    "black": CSS_COLOR_NAME_TO_HEX["black"],
    "darkgray": CSS_COLOR_NAME_TO_HEX["darkgray"],
    "darkgrey": CSS_COLOR_NAME_TO_HEX["darkgrey"],
    "dimgray": CSS_COLOR_NAME_TO_HEX["dimgray"],
    "dimgrey": CSS_COLOR_NAME_TO_HEX["dimgrey"],
    "gainsboro": CSS_COLOR_NAME_TO_HEX["gainsboro"],
    "gray": CSS_COLOR_NAME_TO_HEX["gray"],
    "grey": CSS_COLOR_NAME_TO_HEX["grey"],
    "lightgray": CSS_COLOR_NAME_TO_HEX["lightgray"],
    "lightgrey": CSS_COLOR_NAME_TO_HEX["lightgrey"],
    "silver": CSS_COLOR_NAME_TO_HEX["silver"],
    "darkslategray": CSS_COLOR_NAME_TO_HEX["darkslategray"],
    "darkslategrey": CSS_COLOR_NAME_TO_HEX["darkslategrey"],
    "lightslategray": CSS_COLOR_NAME_TO_HEX["lightslategray"],
    "lightslategrey": CSS_COLOR_NAME_TO_HEX["lightslategrey"],
    "slategray": CSS_COLOR_NAME_TO_HEX["slategray"],
    "slategrey": CSS_COLOR_NAME_TO_HEX["slategrey"],
}
"""A map of gray CSS color names to their hex values."""


def _clamp(
    t: RealNumber, minimum: RealNumber = 0, maximum: RealNumber = 1
) -> RealNumber:
    return min(maximum or 1, max(minimum or 0, t))


def _rem_euclid(lhs: RealNumber, rhs: RealNumber) -> RealNumber:
    abs_rhs = abs(rhs)
    return lhs - abs_rhs * (lhs // abs_rhs)


class ColorRangeError(ValueError):
    """Raised when a color value is out of the valid range."""

    def __init__(self, message: str | None = None) -> None:
        """Raise when a color value is out of the valid range.

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
            ColorRangeError: If any of the RGB components are out of the valid range.
        """
        if any(x < 0 or x > RGB_MAX for x in (r, g, b)):
            raise ColorRangeError("RGB value out of valid range (0-255)")

        self.__r = r
        self.__g = g
        self.__b = b

    def invert(self, /) -> Color3:
        """Invert this color.

        Returns:
            Color3: The inverted color.
        """
        return Color3(
            abs(RGB_MAX - self.__r), abs(RGB_MAX - self.__g), abs(RGB_MAX - self.__b)
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

    @staticmethod
    def get_color_name(hex6: str, /) -> str | None:
        """Get the color name corresponding to the 6-digit hex value.

        Args:
            hex6 (str): The hex color.

        Returns:
            str | None: The color name, if it exists, otherwise None.
        """
        hex6 = hex6.lstrip("#")
        if hex6 in CSS_COLOR_NAME_TO_HEX.values():
            return next(k for k, v in CSS_COLOR_NAME_TO_HEX.items() if v == hex6)
        return None

    @staticmethod
    def validate_hex(hex6: str, /) -> bool:
        """Determine if the given 6-digit hex value is valid.

        Args:
            hex6 (str): The hex value to validate.

        Returns:
            bool: Whether the hex is valid.
        """
        return bool(re.match(r"^[A-Fa-f0-9]{6}$", hex6.lstrip("#")))

    @staticmethod
    def validate_rgb(r: int, g: int, b: int, /) -> bool:
        """Determine if the given RGB color is valid.

        Args:
            r (int): The red component.
            g (int): The green component.
            b (int): The blue component.

        Returns:
            bool: Whether the RGB color is valid.
        """
        return all(0 <= v <= RGB_MAX for v in (r, g, b))

    @classmethod
    def random(cls, /) -> Color3:
        """Create a Color3 with a random value.

        Returns:
            Color3: The new color.
        """
        return Color3(
            secrets.randbelow(RGB_MAX + 1),
            secrets.randbelow(RGB_MAX + 1),
            secrets.randbelow(RGB_MAX + 1),
        )

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
        if name.strip() not in CSS_COLOR_NAME_TO_HEX:
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
        hex6 = hex6.strip("#")
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
            round((rp + m) * RGB_MAX),
            round((gp + m) * RGB_MAX),
            round((bp + m) * RGB_MAX),
        )

    def as_discord_color(self) -> discord.Color:
        """Get this color as a discord.py Color.

        Returns:
            discord.Color: The Discord Color.
        """
        return discord.Color.from_rgb(self.__r, self.__g, self.__b)

    def as_rgb(self) -> tuple[int, int, int]:
        """Get this color as an RGB tuple.

        Returns:
            tuple[int, int, int]: The RGB tuple.
        """
        return self.__r, self.__g, self.__b

    def as_hex6(self) -> str:
        """Get this color as a 6-digit hex string.

        Returns:
            str: The 6-digit hex string.
        """
        return f"{self.__r:02x}{self.__g:02x}{self.__b:02x}".lower()

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


def generate_color_image(color: Color3, /) -> BytesIO:
    """Generate a solid color image from the given color.

    Args:
        color (Color3): The color.

    Returns:
        BytesIO: The bytes of the generated image.
    """
    rgb = color.as_rgb()

    # Create a 100x100 pixel image with the specified RGB color
    img = Image.new("RGB", (100, 100), (rgb[0], rgb[1], rgb[2]))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr
