from pathlib import Path
from typing import Final

__author__: Final[str]
__license__: Final[str]

class DatabaseError(Exception): ...

DB_DIR: Final[Path]
