"""Information about CatBot and its run conditions."""

from datetime import UTC, datetime
from pathlib import Path
from platform import platform
from sys import version_info

from discord import version_info as discord_version_info

__author__ = "Gavin Borne"
__license__ = "MIT"

_SECONDS_PER_HOUR = 3600
_SECONDS_PER_MINUTE = 60
_HOURS_PER_DAY = 24
_MINUTES_PER_HOUR = 60
_MICROSECONDS_PER_SECOND = 1000000

START_TIME = datetime.now(UTC)
"""The time the bot was started."""

HOST = platform()
"""Information about the device hosting CatBot."""

PYTHON_VERSION = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
"""The current Python version running CatBot."""

DISCORD_DOT_PY_VERSION = (
    f"{discord_version_info.major}.{discord_version_info.minor}"
    f".{discord_version_info.micro}"
)
"""The current discord.py version running CatBot."""

CAT_GUILD_ID = 857065913568460801
"""The ID of the cat guild."""

BOT_APP_ID = 1303870147873996902
"""The app ID of CatBot."""

PROTOTYPE_BOT_APP_ID = 1437156873722921053
"""The app ID of the testing bot."""

VERSION = "v1.0.0"
"""The current release version of CatBot."""


def _get_dependencies() -> list[str]:
    path = Path("requirements.txt")
    if not path.is_file():
        raise FileNotFoundError(path)

    # get dependencies from requirements.txt
    dependencies: list[str] = []
    with path.open(encoding="utf-8") as file:
        dependencies.extend(line.strip() for line in file)
    return dependencies


DEPENDENCIES = _get_dependencies()
"""All the dependencies CatBot relies on."""


def get_uptime() -> str:
    """Get the uptime of the bot as a string.

    Returns:
        str: The uptime of the bot.
    """
    uptime = datetime.now(UTC) - START_TIME
    days = uptime.days
    hours = (uptime.seconds // _SECONDS_PER_HOUR) % _HOURS_PER_DAY
    minutes = (uptime.seconds // _SECONDS_PER_MINUTE) % _MINUTES_PER_HOUR
    seconds = uptime.seconds % _SECONDS_PER_MINUTE
    microseconds = uptime.microseconds % _MICROSECONDS_PER_SECOND
    return (
        f"{days} days, {hours} hours, {minutes} minutes, "
        f"{seconds} seconds, {microseconds} microseconds"
    )
