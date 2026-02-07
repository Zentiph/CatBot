"""Types for checks."""

from collections.abc import Callable
from typing import Any, Protocol, TypeVar

__author__ = "Gavin Borne"
__license__ = "MIT"

# had to repurpose these because discord.py doesn't directly export them
# for some ungodly reason (why...?)


F = TypeVar("F", bound=Callable[..., Any])


class CheckDecorator(Protocol):
    """A protocol mimicking discord.py's Check."""

    def __call__(self, func: F, /) -> F:
        """Run the check on a coroutine or command.

        Args:
            func (F): The coroutine or command.
        """
        ...
