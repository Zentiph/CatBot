"""Help info registration for bot commands."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, ParamSpec, Protocol, TypeVar, cast, runtime_checkable

__author__ = "Gavin Borne"
__license__ = "MIT"

P = ParamSpec("P")
T_co = TypeVar("T_co", covariant=True)

Category = Literal["Color", "Fun", "Help", "Utilities"]

HELP_EXTRAS_KEY = "catbot_help"
"""The key to use when cloning HelpInfo into discord.py command extras."""


@runtime_checkable
class HasHelpInfo(Protocol[P, T_co]):
    """A protocol ensuring a callable object has a __help_info__ field."""

    __help_info__: HelpInfo

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co:
        """HelpInfo is attached to callable discord.py command declarations."""
        ...


@dataclass(frozen=True, slots=True)
class HelpInfo:
    """Help information for a command."""

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
) -> Callable[[Callable[P, T_co]], HasHelpInfo[P, T_co]]:
    """Decorator to add help info to a slash command.

    Args:
        category (Category): The category the command lives in.
        summary (str | None, optional): A sentence-summary of the command.
            If None, uses the app command description. Defaults to None.
        examples (tuple[str] | None, optional): Examples of how to use the command.
            Defaults to None.
        notes (str | None, optional): Any special notes about the command.
            Defaults to None.

    Returns:
        Callable[[Callable[P, T_co]], HasHelpInfo[P, T_co]]:
            The decorated command function.
    """

    def decorator(func: Callable[P, T_co]) -> HasHelpInfo[P, T_co]:
        f = cast(HasHelpInfo[P, T_co], func)
        f.__help_info__ = HelpInfo(category, summary, examples, notes)
        return f

    return decorator
