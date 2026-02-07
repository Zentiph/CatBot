"""Database tools for FizzBuzz."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = [
    "DB_DIR",
    "GuildSettings",
    "SettingsStore",
    "settings_store",
    "wrapped",
]

from . import wrapped
from .db import DB_DIR
from .settings import GuildSettings, SettingsStore, settings_store
