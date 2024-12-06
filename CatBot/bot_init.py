"""
bot_init.py
Bot initialization code.
"""

import logging
from argparse import ArgumentParser

import discord
from discord.ext.commands import Bot

from .logging_formatting import LOGGING_FORMAT, ColorFormatter

LOG_FILE = "logs.log"
DEFAULT_EMBED_COLOR = discord.Color(int("ffffff", 16))
LOGGING_CHANNEL = 1306045987319451718
MODERATOR_ROLES = ("Owner", "Management", "Mod")


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


def config_logging(parser: ArgumentParser, /) -> None:
    """
    Config logging settings using command-line arguments.

    CLI args are:
    --logfile {str}
    --testing {store_true}
    --nostreamlogging {store_true}

    Defaults are:
    --logfile logs.log

    :param parser: ArgumentParser to get arg values from
    :type parser: ArgumentParser
    """

    args = parser.parse_args()
    log_file = args.logfile if args.logfile else LOG_FILE
    if args.nostreamlogging:
        handlers = [logging.FileHandler(log_file)]
    else:
        sh = logging.StreamHandler()
        sh.setFormatter(ColorFormatter())
        handlers = [
            logging.FileHandler(log_file),
            sh,  # type: ignore
        ]

    logging.basicConfig(
        level=logging.INFO,
        format=LOGGING_FORMAT,
        handlers=handlers,  # type: ignore
    )

    logging.info(
        "Logging config: logfile=%s, nostreamlogging=%s", log_file, args.nostreamlogging
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
