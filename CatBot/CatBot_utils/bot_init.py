"""
bot_init.py
Bot initialization code.
"""

from argparse import ArgumentParser

import discord
from discord import app_commands
from discord.ext.commands import Bot
from requests import Timeout

from . import pawprints
from .logging_formatting import ColorFormatter

LOG_FILE = "logs.log"
DEFAULT_EMBED_COLOR = discord.Color(int("ffffff", 16))
LOGGING_CHANNEL = 1306045987319451718
MANAGEMENT_ROLES = ("Owner", "Management")
MODERATOR_ROLES = ("Owner", "Management", "Mod")
CAT_API_SEARCH_LINK = "https://api.thecatapi.com/v1/images/search"
APP_COMMAND_ERRORS = (
    app_commands.errors.CheckFailure,
    discord.Forbidden,
    OverflowError,
    Timeout,
)


def get_version() -> str:
    """
    Get CatBot's current version.

    :return: Version
    :rtype: str
    """

    with open("changelog.md", encoding="utf8") as file:
        line = file.readline()
        while not line.startswith("## v"):
            line = file.readline()

        return line.split(" ")[1].strip()


VERSION = get_version()


def initialize_bot() -> Bot:
    """
    Initialize and return the bot.

    :return: Bot
    :rtype: Bot
    """

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.presences = True
    return Bot(command_prefix="!", intents=intents)


def initialize_cli_arg_parser() -> ArgumentParser:
    """
    Initialize the CLI arg parser and return it.

    :return: Arg parser
    :rtype: argparse.ArgumentParser
    """

    parser = ArgumentParser(description="Run CatBot with optional logging arguments")
    parser.add_argument(
        "--logfile",
        type=str,
        help="Path to the file where logs will be written, defaults to 'logs.log'",
    )
    parser.add_argument(
        "--nostreamlogging", action="store_true", help="Disable console logging"
    )
    parser.add_argument(
        "--tokenoverride",
        type=str,
        help="New token to override the default token, "
        + "primarily for testing under a different app than the main app",
    )
    parser.add_argument(
        "--testing", action="store_true", help="Launch the bot in testing mode"
    )
    parser.add_argument(
        "--coloredlogs",
        action="store_true",
        help="Launch the terminal in colored logging mode",
    )

    return parser


def get_token_from_env() -> str:
    """
    Get CatBot's token from the .env file.

    :return: CatBot token
    :rtype: str
    """

    with open(".env", encoding="utf8") as file:
        line = file.readline()
        while not line.startswith("TOKEN="):
            line = file.readline()
        index = line.find("=")

    return line[index + 1 :].strip().strip('"')


def get_cat_api_key_from_env() -> str:
    """
    Get CatBot's Cat API key from the .env file.

    :return: Cat API key
    :rtype: str
    """

    with open(".env", encoding="utf8") as file:
        line = file.readline()
        while not line.startswith("CAT_API_KEY="):
            line = file.readline()
        index = line.find("=")

    return line[index + 1 :].strip().strip('"')


def config_logging(parser: ArgumentParser, /) -> None:
    """
    Config logging settings using command-line arguments.

    CLI args are:
    --logfile {str}
    --testing {store_true}
    --nostreamlogging {store_true}
    --coloredlogs {store_true}

    Defaults are:
    --logfile logs.log

    :param parser: ArgumentParser to get arg values from
    :type parser: ArgumentParser
    """

    args = parser.parse_args()
    log_file = args.logfile if args.logfile else LOG_FILE

    if args.nostreamlogging:
        outputs = [pawprints.FileOutput(log_file)]
    else:
        stream_output = pawprints.StreamOutput()
        if args.coloredlogs:
            stream_output.formatter = ColorFormatter()
        outputs = [
            pawprints.FileOutput(log_file),
            stream_output,  # type: ignore
        ]

    pawprints.config_root(
        level=pawprints.CALL,
        outputs=outputs,
    )

    pawprints.setup(
        f"Logging config: logfile={log_file}, testing={args.testing}, "
        + f"nostreamlogging={args.nostreamlogging}, coloredlogs={args.coloredlogs}"
    )


def get_token(parser: ArgumentParser, /) -> str:
    """
    Get the token to use depending on whether
    --tokenoverride was passed to this module.

    :param parser: Argument parser to get arg values from
    :type parser: ArgumentParser
    :return: Token
    :rtype: str
    """

    args = parser.parse_args()
    return args.tokenoverride if args.tokenoverride else get_token_from_env()


async def handle_app_command_error(
    interaction: discord.Interaction, error: Exception
) -> None:
    """
    Handle an app command error.
    Supported/expected errors are defined in the APP_COMMAND_ERRORS constant.

    :param interaction: Interaction instance
    :type interaction: discord.Interaction
    :param error: The error that occurred
    :type error: AppCommandError | Exception
    """

    async def try_response(message: str, ephemeral: bool = True) -> None:
        """
        Attempt to respond with the given message.
        If the response was deferred, send it with a followup instead.

        :param message: Response message
        :type message: str
        :param ephemeral: Whether the message is ephemeral, defaults to True
        :type ephemeral: bool, optional
        """

        try:
            await interaction.response.send_message(message, ephemeral=ephemeral)
        except discord.errors.InteractionResponded:
            await interaction.followup.send(message, ephemeral=ephemeral)

    if error not in APP_COMMAND_ERRORS:  # Unintentional error
        pawprints.error(f"An error occurred: {error}")
        await try_response(
            "An unknown error occurred. Contact @zentiph to report this please!"
        )

    if isinstance(error, app_commands.errors.CheckFailure):  # Restricted command
        pawprints.info(
            f"Unauthorized user {interaction.user} attempted to use a restricted command",
        )
        await try_response("You do not have permission to use this command.")

    elif isinstance(error, discord.Forbidden):
        pawprints.warning(
            "Attempted to perform a command with inadequate permissions allotted to the bot"
        )
        await try_response("I do not have permissions to perform this command.")

    elif isinstance(error, OverflowError):
        pawprints.info("Overflow error occurred during a calculation")
        await try_response(
            "This calculation caused an arithmetic overflow. Try using smaller numbers."
        )

    elif isinstance(error, Timeout):
        pawprints.warning("Timeout error occurred during HTTP request")
        await try_response(
            "An attempt to communicate with an external API "
            + "has taken too long, and has been canceled."
        )
