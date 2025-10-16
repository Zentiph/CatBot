"""
The entrypoint to run CatBot from.
"""

import logging
import asyncio
from pathlib import Path

from argparse import ArgumentParser, BooleanOptionalAction
import discord
from discord import app_commands
from discord.ext import commands
from requests import Timeout
from sys import exit as ex


from CatBot import pawprints, env

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
    parser.add_argument(
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


async def setup(logfile: Path) -> None:
    with logfile.open("w", encoding="utf8"):
        logging.info(f"Log file {logfile} cleared")

    if args.debug:
        await bot.load_extension("CatBot.experiments.experimental")

    await bot.load_extension("CatBot.color.color")
    await bot.load_extension("CatBot.date_time.date_time")
    await bot.load_extension("CatBot.fun.fun")
    await bot.load_extension("CatBot.help.help")
    await bot.load_extension("CatBot.management.management")
    await bot.load_extension("CatBot.management.moderation")
    await bot.load_extension("CatBot.math.maths")
    await bot.load_extension("CatBot.math.stats")
    await bot.load_extension("CatBot.rand.rand")


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


if __name__ == "__main__":
    main()
