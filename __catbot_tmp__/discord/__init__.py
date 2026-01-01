"""A collection of all the Discord-related functionality for CatBot."""

__author__ = "Gavin Borne"
__license__ = "MIT"

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
