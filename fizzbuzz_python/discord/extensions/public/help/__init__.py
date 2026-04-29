"""Help commands."""

__author__ = "Gavin Borne"
__license__ = "MIT"

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
