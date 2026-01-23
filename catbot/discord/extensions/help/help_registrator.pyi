from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Any,
    Final,
    Literal,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

import discord
from discord import app_commands

__author__: Final[str]
__license__: Final[str]

P = ParamSpec("P")
T_co = TypeVar("T_co", covariant=True)

AppCommand: TypeAlias = (
    app_commands.Command[Any, ..., Any] | app_commands.Group | app_commands.ContextMenu
)
Category: TypeAlias = Literal["Color", "Fun", "Help", "Utilities"]

COMMAND_CATEGORIES: Final[tuple[Category]]

@runtime_checkable
class HasHelpInfo(Protocol[P, T_co]):
    __help_info__: HelpInfo
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co: ...

@dataclass(frozen=True, slots=True)
class HelpInfo:
    category: Category
    summary: str | None
    params: dict[str, str | None]
    examples: tuple[str, ...] | None
    notes: tuple[str, ...] | None

def build_command_info_str(command: AppCommand, help_info: HelpInfo, /) -> str: ...
def build_help_homepage() -> tuple[discord.Embed, discord.File]: ...
def help_info(
    category: Category,
    /,
    summary: str | None = None,
    *,
    params: dict[str, str | None] | None = None,
    examples: tuple[str, ...] | None = None,
    notes: tuple[str, ...] | None = None,
) -> Callable[[Callable[P, T_co]], HasHelpInfo[P, T_co]]: ...
def get_help_info(obj: object, /) -> HelpInfo | None: ...
