"""Help commands."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = [
    "Category",
    "HasHelpInfo",
    "HelpInfo",
    "get_help_info",
    "help_info",
]

from .help_registrator import (
    Category,
    HasHelpInfo,
    HelpInfo,
    get_help_info,
    help_info,
)
