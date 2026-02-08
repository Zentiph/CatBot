"""Types for checks."""

from collections.abc import Callable
from typing import Any, TypeVar

__author__ = "Gavin Borne"
__license__ = "MIT"

T = TypeVar("T")

CheckT = Callable[[T], T]
Check = CheckT[Any]
