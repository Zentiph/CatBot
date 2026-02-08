from typing import Final

from discord import app_commands

from .types import Check

__author__: Final[str]
__license__: Final[str]

class Unauthorized(app_commands.CheckFailure):
    def __init__(self, message: str | None = None) -> None: ...

def admin_only() -> Check: ...
def owner_only() -> Check: ...
