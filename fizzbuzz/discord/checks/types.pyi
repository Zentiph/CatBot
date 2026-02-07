from collections.abc import Callable
from typing import Any, Final, Protocol, TypeVar

__author__: Final[str]
__license__: Final[str]

F = TypeVar("F", bound=Callable[..., Any])

class CheckDecorator(Protocol):
    """A protocol mimicking discord.py's Check."""

    def __call__(self, func: F, /) -> F:
        """Run the check on a coroutine or command.

        Args:
            func (F): The coroutine or command.
        """
        ...
