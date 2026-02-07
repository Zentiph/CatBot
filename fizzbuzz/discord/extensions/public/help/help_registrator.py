"""Help info registration for bot commands."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Any,
    Literal,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    get_args,
    runtime_checkable,
)

import discord
from discord import app_commands

from ....interaction import build_response_embed
from ....ui.emoji import Visual

__author__ = "Gavin Borne"
__license__ = "MIT"

P = ParamSpec("P")
T_co = TypeVar("T_co", covariant=True)

AppCommand = (
    app_commands.Command[Any, ..., Any] | app_commands.Group | app_commands.ContextMenu
)
Category = Literal["Color", "Fun", "Help", "Utilities"]

COMMAND_CATEGORIES: tuple[Category] = get_args(Category)
"""All command categories."""


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
    params: dict[str, str | None]
    examples: tuple[str, ...] | None
    notes: tuple[str, ...] | None


def build_command_info_str(command: AppCommand, help_info: HelpInfo, /) -> str:
    """Create an info string for a command.

    Args:
        command (AppCommand): The command.
        help_info (HelpInfo): The help info of the command.

    Returns:
        str: The formatted info string.
    """
    out = (
        help_info.summary or getattr(command, "description", None) or "(no description)"
    )

    if isinstance(command, app_commands.Command):
        out += "\n**Parameters:**"
        for param in command.parameters:
            # default to specially defined param description,
            # then fallback to Discord registered description
            out += (
                f"\n`{param.name}`: "
                f"{help_info.params.get(param.name) or param.description}"
            )

    if help_info.examples:
        out += "\n**Examples:**\n" + "\n".join(f"`{ex}`" for ex in help_info.examples)
    if help_info.notes:
        out += "\n**Notes:**\n" + "\n".join(note for note in help_info.notes)

    return out


def build_help_homepage() -> tuple[discord.Embed, discord.File]:
    """Build the help homepage.

    Returns:
        tuple[discord.Embed, discord.File]: The embed and its icon.
    """
    embed, icon = build_response_embed(
        title=f"{Visual.QUESTION_MARK} FizzBuzz Help",
        description="Here's a brief overview of how to use FizzBuzz!",
    )
    embed.add_field(
        name="Usage",
        value="FizzBuzz operates purely with slash commands.\n"
        "Type `/` followed by the name of the command you want to use.\n"
        "To view a list of all commands, type `/`, "
        "and then find FizzBuzz in the menu that appears.",
    )
    embed.add_field(
        name="Command Help",
        value="For help regarding a specific command, "
        "use /help and enter a command name.",
    )
    embed.add_field(
        name="Bugs/Issues",
        value="If you find a bug or issue, please "
        "[create a GitHub issue](https://github.com/Zentiph/FizzBuzz/issues) "
        "or contact @viiviiviiviiaan.",
    )

    return embed, icon


def help_info(
    category: Category,
    /,
    summary: str | None = None,
    *,
    params: dict[str, str | None] | None = None,
    examples: tuple[str, ...] | None = None,
    notes: tuple[str, ...] | None = None,
) -> Callable[[Callable[P, T_co]], HasHelpInfo[P, T_co]]:
    """Decorator to add help info to a slash command.

    Args:
        category (Category): The category the command lives in.
        summary (str | None, optional): A sentence-summary of the command.
            If None, uses the app command description. Defaults to None.
        params (dict[str, str | None] | None, optional): A map of parameter names to
            their descriptions. Defaults to None.
        examples (tuple[str] | None, optional): Examples of how to use the command.
            Defaults to None.
        notes (tuple[str, ...] | None, optional): Any special notes about the command.
            Defaults to None.

    Returns:
        Callable[[Callable[P, T_co]], HasHelpInfo[P, T_co]]:
            The decorated command function.
    """

    def decorator(func: Callable[P, T_co]) -> HasHelpInfo[P, T_co]:
        f = cast(HasHelpInfo[P, T_co], func)
        f.__help_info__ = HelpInfo(category, summary, params or {}, examples, notes)
        return f

    return decorator


def get_help_info(obj: object, /) -> HelpInfo | None:
    """Attempt to get the help info of an object.

    Args:
        obj (object): The object to get the help info of.

    Returns:
        HelpInfo | None: The help info if found, otherwise None.
    """
    # for app command objects, help info lives on the callback
    callback = getattr(obj, "callback", None)
    return cast(HelpInfo | None, getattr(callback, "__help_info__", None))
