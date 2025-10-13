"""
Functionality for reading and creating the .env file.
"""

from pathlib import Path
from typing import Callable, TypeVar

__author__ = "Gavin Borne"
__license__ = "MIT"

T = TypeVar("T")


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

                env_dict[fields[0]] = fields[1]

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
