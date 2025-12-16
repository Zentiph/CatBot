from typing import Final

__author__: Final[str]
__license__: Final[str]

__all__: Final[list[str]]

from . import interaction as interaction, ui as ui, views as views
from .info import (
    BOT_APP_ID as BOT_APP_ID,
    DEPENDENCIES as DEPENDENCIES,
    DISCORD_DOT_PY_VERSION as DISCORD_DOT_PY_VERSION,
    HOST as HOST,
    PROTOTYPE_BOT_APP_ID as PROTOTYPE_BOT_APP_ID,
    PYTHON_VERSION as PYTHON_VERSION,
    START_TIME as START_TIME,
    VERSION as VERSION,
    get_uptime as get_uptime,
)
