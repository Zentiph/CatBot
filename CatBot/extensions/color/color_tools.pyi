# pylint:disable=all

from typing import Final

__author__: Final[str]
__license__: Final[str]

REDS: Final[dict[str, str]]
PINKS: Final[dict[str, str]]
ORANGES: Final[dict[str, str]]
YELLOWS: Final[dict[str, str]]
PURPLES: Final[dict[str, str]]
GREENS: Final[dict[str, str]]
BLUES: Final[dict[str, str]]
BROWNS: Final[dict[str, str]]
WHITES: Final[dict[str, str]]
GRAYS: Final[dict[str, str]]
COLORS: Final[dict[str, str]]

def is_hex_value(hex6: str) -> bool: ...
def is_rgb_value(value: int) -> bool: ...
def random_rgb(*, seed: str | None = None) -> tuple[int, int, int]: ...
def invert_rgb(r: int, g: int, b: int) -> tuple[int, int, int]: ...
def invert_hex(hex6: str) -> str: ...
def hex2rgb(hex6: str) -> tuple[int, int, int]: ...
def rgb2hex(r: int, g: int, b: int) -> str: ...
def random_hex() -> str: ...
