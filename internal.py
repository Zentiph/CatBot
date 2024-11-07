"""
internal.py
Internal constants and functions for CatBot.
"""

from discord import Color


LOG_FILE = "logs.log"
DEFAULT_EMBED_COLOR = Color(int("575afa", 16))


def get_token(*, override: str = ".env") -> str:
    """
    Get CatBot's token.

    :param override: Override file to provide a different token, defaults to ".env"
    :type override: str
    :return: CatBot token
    :rtype: str
    """

    with open(override, encoding="utf8") as file:
        line = file.readline()
        while not line.startswith("TOKEN="):
            line = file.readline()
        index = line.find("=")

    return line[index + 1 :].strip().strip('"')
