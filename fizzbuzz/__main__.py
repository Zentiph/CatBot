"""The entrypoint to run FizzBuzz from."""

from argparse import ArgumentParser, BooleanOptionalAction
import asyncio
from importlib import import_module
import logging
import os
from pathlib import Path
import pkgutil
from sys import exit as ex

import discord
from discord import app_commands
from discord.ext import commands
from requests import Timeout

from fizzbuzz import log_handler
from fizzbuzz.discord.interaction import report
from fizzbuzz.discord.ui.emoji import Status

__author__ = "Gavin Borne"
__license__ = "MIT"


def init_arg_parser() -> ArgumentParser:
    """Initialize the argument parser.

    Returns:
        ArgumentParser: The argument parser.
    """
    arg_parser = ArgumentParser(description="Run FizzBuzz with optional arguments")
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
    arg_parser.add_argument(
        "--show-env",
        action="store_true",
        help="Show the environment variables related to the bot on startup",
    )
    return arg_parser


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    allowed_contexts=discord.app_commands.AppCommandContext(
        guild=True, dm_channel=True, private_channel=True
    ),
    allowed_installs=discord.app_commands.AppInstallationType(guild=True, user=True),
)

parser = init_arg_parser()
args = parser.parse_args()


@bot.event
async def on_ready() -> None:
    """Sync and register slash commands."""
    await bot.tree.sync()

    if args.debug:
        await bot.change_presence(activity=discord.Game(name="⚠ TESTING ⚠"))
        logging.warning(
            "The application has been started in testing mode; "
            "ignore if this is intentional"
        )
    else:
        await bot.change_presence(activity=discord.Game(name="/help"))

    if bot.user is None:
        logging.error("Log in failed")
        return

    logging.info(f"Logged in as {bot.user.name} and slash commands synced\n")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    """Handle app command errors.

    Args:
        interaction (discord.Interaction): The interaction instance.
        error (app_commands.AppCommandError): The error.
    """
    if isinstance(error, app_commands.errors.CheckFailure):  # restricted command
        logging.info(
            f"Unauthorized user {interaction.user} attempted"
            " to use a restricted command",
        )
        await report(
            interaction,
            "You do not have permission to use this command.",
            Status.FAILURE,
        )
        return

    if isinstance(error, discord.Forbidden):
        logging.warning(
            "Attempted to perform a command with inadequate "
            "permissions allotted to the bot"
        )
        await report(
            interaction,
            "I do not have permissions to perform this command.",
            Status.WARNING,
        )
        return

    if isinstance(error, Timeout):
        logging.warning("Timeout error occurred during HTTP request")
        await report(
            interaction,
            "An attempt to communicate with an external API "
            "has taken too long, and has been canceled.",
            Status.ERROR,
        )
        return

    logging.error(f"An error occurred: {error}")
    await report(
        interaction,
        "An unknown error occurred. Contact @zentiph to report this please!",
        Status.ERROR,
    )


async def load_group(to_bot: commands.Bot, base_pkg: str) -> None:
    """Load a group of extensions from a base package.

    Args:
        to_bot (commands.Bot): The bot to load the extensions to.
        base_pkg (str): The base package of the extension group.
    """
    root = "fizzbuzz.discord.extensions"
    pkg = import_module(root + "." + base_pkg)

    for _, module_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
        if is_pkg:
            continue  # skip sub packages

        full_name = f"{root}.{base_pkg}.{module_name}"
        if not full_name.endswith("_cog"):
            continue

        try:
            await to_bot.load_extension(full_name)
            logging.info(f"Loaded extension: {full_name}")
        except commands.errors.ExtensionAlreadyLoaded:
            logging.debug(f"Already loaded extension: {full_name}, skipping")
        except commands.errors.NoEntryPointError:
            # module didn't have a setup(bot) func
            logging.exception(
                f"Couldn't load extension: {full_name}, "
                "no setup(bot) function present, skipping"
            )
        except (commands.errors.ExtensionNotFound, ModuleNotFoundError):
            logging.exception(f"Extension not found: {full_name}")
        except commands.errors.ExtensionFailed:
            logging.exception(f"Failed to load extension: {full_name}")


async def setup(logfile: Path) -> None:
    """Run setup for the bot.

    Args:
        logfile (Path): The file to output logs to.
    """
    logfile.parent.mkdir(parents=True, exist_ok=True)
    logfile.write_text("", encoding="utf-8")  # clear

    if args.show_env:
        logging.info("Running FizzBuzz with environment variables:")
        logging.info("TOKEN: (hidden)")
        logging.info(f"HTTP_USER_AGENT: {os.getenv('HTTP_USER_AGENT')}")
        logging.info(
            f"HTTP_PER_HOST_MIN_INTERVAL: {os.getenv('HTTP_PER_HOST_MIN_INTERVAL')}"
        )
        logging.info("(Default values will be used if a variable is None.)")

    await load_group(bot, "color")
    await load_group(bot, "fun")
    await load_group(bot, "utilities")

    # load help last for proper command sync
    await load_group(bot, "help")

    if not args.debug:
        # comment this next line out if you don't want to do message metric tracking
        await load_group(bot, "metrics")


def main() -> None:
    """Read CLI args, setup the bot and logging, then run the bot."""
    logfile_path = Path(args.log_file)
    if not logfile_path.is_file():
        logfile_path.touch()

    log_handler.config_logging(
        args.log_file,
        console_logging=args.console_logging,
        colored_logs=args.colored_logs,
        debug=args.debug,
    )

    token = (
        args.token_override if args.token_override is not None else os.getenv("TOKEN")
    )
    if not isinstance(token, str):
        ex("Could not parse token")

    asyncio.run(setup(logfile_path))
    bot.run(token)


main()
