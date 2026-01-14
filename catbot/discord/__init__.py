"""A collection of all the Discord-related functionality for CatBot."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = [
    "BOT_APP_ID",
    "DEPENDENCIES",
    "DISCORD_DOT_PY_VERSION",
    "HOST",
    "PROTOTYPE_BOT_APP_ID",
    "PYTHON_VERSION",
    "START_TIME",
    "VERSION",
    "get_uptime",
    "interaction",
    "ui",
    "views",
]

from . import interaction, ui, views
from .info import (
    BOT_APP_ID,
    DEPENDENCIES,
    DISCORD_DOT_PY_VERSION,
    HOST,
    PROTOTYPE_BOT_APP_ID,
    PYTHON_VERSION,
    START_TIME,
    VERSION,
    get_uptime,
)
