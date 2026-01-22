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

from ...interaction import build_response_embed, safe_edit
from ...ui.emoji import Visual
from ...views import CarouselView

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
    examples: tuple[str, ...] | None
    notes: tuple[str, ...] | None


def build_command_info_str(
    command: AppCommand, help_info: HelpInfo, /, description: str | None = None
) -> str:
    """Create an info string for a command.

    Args:
        command (AppCommand): The command.
        help_info (HelpInfo): The help info of the command.
        description (str | None, optional): The description of the command.
            If None, uses the registered command description. Defaults to None.

    Returns:
        str: The formatted info string.
    """
    out = description or getattr(command, "description", None) or "(no description)"
    if help_info.examples:
        out += "\nExamples:\n" + "\n".join(f"`{ex}`" for ex in help_info.examples)
    if help_info.notes:
        out += "\nNotes:\n" + "\n".join(note for note in help_info.notes)

    return out


def _build_help_category_embed(
    category: Category,
    categories: dict[Category, list[AppCommand]],
    index: int,
) -> tuple[discord.Embed, discord.File]:
    category_title = category.title()
    embed, icon = build_response_embed(
        title=f"{Visual.QUESTION_MARK} {category_title} Help "
        # add 1 to categories to account for homepage
        f"({index + 1}/{len(categories) + 1})",
        description=f"Help page for {category_title} commands",
    )
    for command in categories[category]:
        help_info = get_help_info(command)
        if help_info is None:
            continue

        embed.add_field(
            name=f"/{command.name}",
            value=build_command_info_str(command, help_info),
        )

    return embed, icon


def build_help_homepage(pages: int) -> tuple[discord.Embed, discord.File]:
    """Build the help homepage.

    Args:
        pages (int): The total number of pages for the help view.

    Returns:
        tuple[discord.Embed, discord.File]: The embed and its icon.
    """
    embed, icon = build_response_embed(
        title=f"{Visual.QUESTION_MARK} CatBot Help (1/{pages})",
        description="Here's a brief overview of how to use CatBot!",
    )
    embed.add_field(
        name="Usage",
        value="CatBot operates purely with slash commands.\n"
        "Type `/` followed by the name of the command you want to use.\n"
        "To view a list of all commands, type `/`, "
        "and then find CatBot in the menu that appears.",
    )
    embed.add_field(
        name="Bugs/Issues",
        value="If you find a bug or issue, please "
        "[create a GitHub issue](https://github.com/Zentiph/CatBot/issues) "
        "or contact @viiviiviiviiaan.",
    )

    return embed, icon


class HelpCarouselView(CarouselView):
    """A carousel view for help categories."""

    def __init__(
        self,
        *,
        user: discord.abc.User,
        categories: dict[Category, list[AppCommand]],
        timeout: float | None = 180.0,
    ) -> None:
        """A carousel view for help categories.

        Args:
            user (discord.abc.User): The user who spawned the view.
            categories (dict[Category, list[AppCommand]]): A mapping of categories to
                app commands with help info.
            timeout (float | None, optional): The timeout of the view in seconds.
                Defaults to 180.0.
        """
        self.__categories = categories
        # add 1 to command categories length to account for homepage
        super().__init__(len(COMMAND_CATEGORIES) + 1, user=user, timeout=timeout)

    async def render(self, interaction: discord.Interaction, /) -> None:
        """Render the next help page after a button is pressed.

        Args:
            interaction (discord.Interaction): The interaction instance.
        """
        if self.index == 0:
            embed, icon = build_help_homepage(self.pages)
        else:
            # maintain order by using the tuple rather than the dict
            category = COMMAND_CATEGORIES[self.index - 1]
            embed, icon = _build_help_category_embed(
                category, self.__categories, self.index
            )

        self.sync_buttons()
        await safe_edit(interaction, embed=embed, attachments=[icon], view=self)


def help_info(
    category: Category,
    /,
    summary: str | None = None,
    *,
    examples: tuple[str, ...] | None = None,
    notes: tuple[str, ...] | None = None,
) -> Callable[[Callable[P, T_co]], HasHelpInfo[P, T_co]]:
    """Decorator to add help info to a slash command.

    Args:
        category (Category): The category the command lives in.
        summary (str | None, optional): A sentence-summary of the command.
            If None, uses the app command description. Defaults to None.
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
        f.__help_info__ = HelpInfo(category, summary, examples, notes)
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
