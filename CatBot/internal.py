"""
internal.py
Internal constants and functions for CatBot.
"""

import logging
from argparse import ArgumentParser

import discord
from discord.ext.commands import Bot


LOG_FILE = "logs.log"
DEFAULT_EMBED_COLOR = discord.Color(int("ffffff", 16))
LOGGING_FORMAT = (
    "%(asctime)s | [%(levelname)s] %(name)s - %(message)s (%(filename)s:%(lineno)d)"
)
TIME_MULTIPLICATION_TABLE = {
    "seconds": 1,
    "minutes": 60,
    "hours": 3600,
    "days": 86400,
}
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


def generate_ansi(r: int, g: int, b: int) -> str:
    """
    Generate an ANSI code given the RGB color.

    :param r: R value
    :type r: int
    :param g: G value
    :type g: int
    :param b: B value
    :type b: int
    :return: ANSI code matching the RGB color
    :rtype: str
    """

    return f"\x1b[38;2;{r};{g};{b}m"


class ColorFormatter(logging.Formatter):
    """
    Custom color formatter for logging stream outputs.
    """

    BOLD = "\x1b[1m"
    DEBUG = generate_ansi(166, 227, 161)
    INFO = generate_ansi(93, 157, 243)
    WARNING = generate_ansi(255, 255, 0)
    ERROR = generate_ansi(255, 0, 0)
    FATAL = generate_ansi(255, 0, 0) + BOLD
    RESET = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: DEBUG + LOGGING_FORMAT + RESET,
        logging.INFO: INFO + LOGGING_FORMAT + RESET,
        logging.WARNING: WARNING + LOGGING_FORMAT + RESET,
        logging.ERROR: ERROR + LOGGING_FORMAT + RESET,
        logging.CRITICAL: FATAL + LOGGING_FORMAT + RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Apply the format to the log message.

        :param record: Logging record
        :type record: logging.LogRecord
        :return: Formatted log
        :rtype: str
        """

        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def generate_image_file(filepath: str) -> discord.File:
    """
    Generate an image File given `filepath`.
    The image's name is "image.png".

    :param filepath: Path to an image
    :type filepath: str
    :return: Discord image File
    :rtype: discord.File
    """

    if not any(
        (
            (
                filepath.endswith(".jpg"),
                filepath.endswith(".jpeg"),
                filepath.endswith(".png"),
            )
        )
    ):
        raise ValueError("Image filepath should be a .jpg or .png file")

    return discord.File(filepath, filename="image.png")
