from collections.abc import Callable
from typing import Any, Final, TypeAlias, TypeVar

__author__: Final[str]
__license__: Final[str]

T = TypeVar("T")

CheckT: TypeAlias = Callable[[T], T]
Check: TypeAlias = CheckT[Any]
