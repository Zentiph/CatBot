"""All the functionality for FizzBuzz."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = ["discord", "log_handler"]


from . import discord
from .util import log_handler
