from typing import Final

__author__: Final[str]
__license__: Final[str]

__all__: Final[list[str]]

from . import wrapped as wrapped
from .db import DB_DIR as DB_DIR
from .settings import (
    SettingsManager as SettingsManager,
    settings_manager as settings_manager,
)
