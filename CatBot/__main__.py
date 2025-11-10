"""
The entrypoint to run CatBot from.
"""

import asyncio
import logging
import pkgutil
from argparse import ArgumentParser, BooleanOptionalAction
from importlib import import_module
from pathlib import Path
from sys import exit as ex

import discord
from discord import app_commands
from discord.ext import commands
from requests import Timeout

from CatBot import env, pawprints

__author__ = "Gavin Borne"
__license__ = "MIT"

APP_COMMAND_ERRORS = (
    app_commands.errors.CheckFailure,
    discord.Forbidden,
    OverflowError,
    Timeout,
)


def init_bot() -> commands.Bot:
    """Initialize the bot.

    Returns:
        commands.Bot: The bot instance.
    """

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.presences = True
    return commands.Bot(command_prefix="!", intents=intents)


def init_arg_parser() -> ArgumentParser:
    """Initialize the argument parser.

    Returns:
        ArgumentParser: The argument parser.
    """

    arg_parser = ArgumentParser(description="Run CatBot with optional arguments")
    arg_parser.add_argument(
        "--log-file",
        type=str,
        default="logs.log",
        help="Path to the file where logs will be written, defaults to 'logs.log'",
    )
    arg_parser.add_argument(
        "--console-logging",
        action=BooleanOptionalAction,
        default=True,
        help="Enable/disable console logging, on by default",
    )
    arg_parser.add_argument(
        "--token-override",
        type=str,
        help="A token to override the token from .env"
        " (for testing under a different app)",
    )
    arg_parser.add_argument(
        "--debug",
        action="store_true",
        help="Launch the bot in debug mode (debug logs enabled)",
    )
    arg_parser.add_argument(
        "--colored-logs",
        action=BooleanOptionalAction,
        default=True,
        help="Use/don't use ANSI color formatting in the console, on by default",
    )
    return arg_parser


bot = init_bot()
parser = init_arg_parser()
args = parser.parse_args()


@bot.event
async def on_ready() -> None:
    """
    Sync and register slash commands.
    """

    await bot.tree.sync()

    if args.debug:
        await bot.change_presence(activity=discord.Game(name="⚠ TESTING ⚠"))
        logging.warning(
            "The application has been started in testing mode; ignore if this is intentional"
        )
    else:
        await bot.change_presence(activity=discord.Game(name="/help"))

    logging.info(f"Logged in as {bot.user.name} and slash commands synced")  # type: ignore
    logging.info("---------------------------------------------")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    """Handle app command errors.

    Args:
        interaction (discord.Interaction): The interaction instance.
        error (app_commands.AppCommandError): The error.
    """

    async def try_response(message: str, ephemeral: bool = True) -> None:
        try:
            await interaction.response.send_message(message, ephemeral=ephemeral)
        except discord.errors.InteractionResponded:
            await interaction.followup.send(message, ephemeral=ephemeral)

    if type(error) not in APP_COMMAND_ERRORS:  # Unintentional error
        logging.error(f"An error occurred: {error}")
        await try_response(
            "An unknown error occurred. Contact @zentiph to report this please!"
        )

    if isinstance(error, app_commands.errors.CheckFailure):  # Restricted command
        logging.info(
            f"Unauthorized user {interaction.user} attempted to use a restricted command",
        )
        await try_response("You do not have permission to use this command.")

    elif isinstance(error, discord.Forbidden):
        logging.warning(
            "Attempted to perform a command with inadequate permissions allotted to the bot"
        )
        await try_response("I do not have permissions to perform this command.")

    elif isinstance(error, OverflowError):
        logging.info("Overflow error occurred during a calculation")
        await try_response(
            "This calculation caused an arithmetic overflow. Try using smaller numbers."
        )

    elif isinstance(error, Timeout):
        logging.warning("Timeout error occurred during HTTP request")
        await try_response(
            "An attempt to communicate with an external API "
            + "has taken too long, and has been canceled."
        )


async def load_group(to: commands.Bot, base_pkg: str) -> None:
    """Load a group of extensions from a base package.

    Args:
        to (commands.Bot): The bot to load the extensions to.
        base_pkg (str): The base package of the extension group.
    """

    pkg = import_module(base_pkg)
    for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
        full_name = f"{base_pkg}.{module_name}"
        try:
            await to.load_extension(full_name)
            logging.info(f"Loaded extension: {full_name}")
        except commands.errors.ExtensionAlreadyLoaded:
            logging.debug(f"Already loaded extension: {full_name}, skipping")
        except commands.errors.NoEntryPointError:
            # Module didn't have a setup(bot) func
            logging.debug(
                f"Couldn't load extension: {full_name}, "
                "no setup(bot) function present, skipping"
            )
        except commands.errors.ExtensionNotFound:
            logging.error(f"Extension not found: {full_name}")
        except commands.errors.ExtensionFailed:
            logging.exception(f"Failed to load extension: {full_name}")


async def setup(logfile: Path) -> None:
    logfile.parent.mkdir(parents=True, exist_ok=True)
    logfile.write_text("", encoding="utf-8")  # clear

    if args.debug:
        await load_group(bot, "experimental")

    await load_group(bot, "color")
    await load_group(bot, "date_time")
    await load_group(bot, "fun")
    await load_group(bot, "help")
    await load_group(bot, "management")
    await load_group(bot, "math")
    await load_group(bot, "rand")


def main():
    """
    Read command-line arguments, setup the bot and logging,
    run any other setup, and run the bot.
    """

    logfile_path = Path(args.log_file)
    if not logfile_path.is_file():
        ex(f"Could not find file '{args.log_file}'")

    pawprints.config_logging(
        args.log_file,
        console_logging=args.console_logging,
        colored_logs=args.colored_logs,
        debug=args.debug,
    )

    try:
        dot_env = env.DotEnv(".env")
    except env.EnvSyntaxError:
        logging.error("The provided .env has syntax errors", exc_info=True)
        ex(
            "Error: Tried to load a .env with invalid syntax. "
            "Check the logs for more details."
        )
    except ValueError:
        logging.error(
            "Tried to load a .env file from a file without .env extension",
            exc_info=True,
        )
        ex(
            "Error: Tried to load a .env file from a file without the .env extension."
            " Check the logs for more details."
        )
    except FileNotFoundError:
        logging.error("Tried to load a .env file that does not exist", exc_info=True)
        ex(
            "Error: Tried to load a .env file that does not exist. "
            "Check the logs for more details."
        )

    token = args.token_override if args.token_override is not None else dot_env["TOKEN"]

    asyncio.run(setup(logfile_path))
    bot.run(token)


main()
