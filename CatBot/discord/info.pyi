"""Information about CatBot and its run conditions."""

from datetime import datetime
from typing import Final

__author__: Final[str]
__license__: Final[str]

START_TIME: Final[datetime]
HOST: Final[str]
PYTHON_VERSION: Final[str]
DISCORD_DOT_PY_VERSION: Final[str]
VERSION: Final[str]
DEPENDENCIES: Final[list[str]]

def get_uptime() -> str: ...
