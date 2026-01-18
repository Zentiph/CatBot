"""All the functionality for CatBot."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = ["discord", "pawprints"]


from . import discord
from .util import pawprints
