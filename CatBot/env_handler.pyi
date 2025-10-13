# pylint:disable=all
from collections.abc import Callable
from typing import TypeVar, Final

__author__: Final[str]
__license__: Final[str]

T = TypeVar("T")

EXPECTED_FIELDS: tuple[str, ...]

class EnvSyntaxError(ValueError): ...

class DotEnv(dict[str, str]):
    def __init__(self, filename: str) -> None: ...
    def get_value_as(self, key: str, coercer: Callable[[str], T]) -> T | None: ...

def patch_env(filename: str, env: DotEnv) -> None: ...
def generate_env() -> None: ...
