"""
Functionality for reading and creating the .env file.
"""

from collections.abc import Callable
from pathlib import Path
from typing import TypeVar


__author__ = "Gavin Borne"
__license__ = "MIT"

T = TypeVar("T")

EXPECTED_FIELDS = ("TOKEN", "CAT_API_KEY")
"""All the fields that are expected to be in the .env file."""


class EnvSyntaxError(ValueError):
    """Raised when a line being parsed from a .env file has invalid syntax."""


class DotEnv(dict[str, str]):
    """A .env file parser that can be accessed like a dictionary."""

    def __init__(self, filename: str) -> None:
        """Parse a .env file and store the data in this instance.

        Args:
            filename (str): The path to the .env file.

        Raises:
            ValueError: If the provided file is not a .env file.
            FileNotFoundError: If the provided file does not exist.
            EnvSyntaxError: If the provided file has syntax errors in it.
        """

        if not filename.endswith(".env"):
            raise ValueError("The file to parse should be a .env file.")

        path = Path(filename)
        if not path.exists():
            raise FileNotFoundError("Provided .env path does not exist.")

        env_dict = {}
        with path.open(mode="r", encoding="utf-8") as file:
            for i, line in enumerate(file):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # ignore empty lines and comments

                fields = line.split("=", maxsplit=1)
                if len(fields) < 2:
                    raise EnvSyntaxError(
                        "Expected value name and value separated by '=' "
                        f"in '{filename}', line {i + 1}"
                    )

                value = fields[1]
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1][1:-1]  # strip leading and ending quotes

                env_dict[fields[0]] = value

        super().__init__(**env_dict)

    def get_value_as(self, key: str, coercer: Callable[[str], T]) -> T | None:
        """Try to get a value as a certain type.

        Args:
            key (str): The key of the value to get.
            coercer (Callable[[str], T]): The coercer function to attempt
                to apply (e.g. int).

        Returns:
            T | None: The result if the coercion was a success, otherwise None.
        """

        try:
            return coercer(self[key])
        except (TypeError, ValueError):
            return None


def patch_env(filename: str, env: DotEnv) -> None:
    if not filename.endswith(".env"):
        raise ValueError("The file to parse should be a .env file.")

    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError("Provided .env path does not exist.")

    with path.open(mode="a", encoding="utf-8") as file:
        for field in EXPECTED_FIELDS:
            if env.get(field) is None:
                file.write(f"{field}= #! value needed !")


def generate_env() -> None:
    with open(".env", mode="x", encoding="utf-8") as file:
        for field in EXPECTED_FIELDS:
            file.write(f"{field}= #! value needed !")
