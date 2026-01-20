from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Final,
    Literal,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

__author__: Final[str]
__license__: Final[str]

P = ParamSpec("P")
T_co = TypeVar("T_co", covariant=True)

Category: TypeAlias = Literal["Color", "Fun", "Help", "Utilities"]

HELP_EXTRAS_KEY: Final[str]

@runtime_checkable
class HasHelpInfo(Protocol[P, T_co]):
    __help_info__: HelpInfo
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co: ...

@dataclass(frozen=True, slots=True)
class HelpInfo:
    category: Category
    summary: str | None
    examples: tuple[str] | None
    notes: str | None

def help_info(
    category: Category,
    /,
    summary: str | None = None,
    *,
    examples: tuple[str] | None = None,
    notes: str | None = None,
) -> Callable[[Callable[P, T_co]], HasHelpInfo[P, T_co]]: ...
