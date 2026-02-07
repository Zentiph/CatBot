"""Bot-wide database specifications."""

import os
from pathlib import Path

__author__ = "Gavin Borne"
__license__ = "MIT"


class DatabaseError(Exception):
    """Raised when a database error occurs."""


_db_dir = os.getenv("DB_DIR")
if _db_dir is None:
    raise DatabaseError("DB_DIR not specified in .env file")

DB_DIR = Path(_db_dir)
"""The path to the directory where the bot's DBs are stored."""

DB_DIR.mkdir(parents=True, exist_ok=True)
