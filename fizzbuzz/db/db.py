"""Bot-wide database specifications."""

from pathlib import Path

__author__ = "Gavin Borne"
__license__ = "MIT"


class DatabaseError(Exception):
    """Raised when a fatal DB issue occurs."""


DB_DIR = Path("data/")
"""The path to the directory where the bot's DBs are stored."""
DB_DIR.mkdir(parents=True, exist_ok=True)
