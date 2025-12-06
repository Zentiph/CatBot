"""A collection of all the Discord-related functionality for CatBot."""

__author__ = "Gavin Borne"
__license__ = "MIT"

__all__ = [
    "DEPENDENCIES",
    "DISCORD_DOT_PY_VERSION",
    "HOST",
    "PYTHON_VERSION",
    "START_TIME",
    "VERSION",
    "get_uptime",
    "interaction",
    "ui",
]

from . import interaction, ui
from .info import (
    DEPENDENCIES,
    DISCORD_DOT_PY_VERSION,
    HOST,
    PYTHON_VERSION,
    START_TIME,
    VERSION,
    get_uptime,
)
