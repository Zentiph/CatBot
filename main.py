"""
main.py
Main file.
"""

import argparse
import logging
from asyncio import run

import discord
from discord import app_commands
from discord.ext import commands

from CatBot.internal import LOG_FILE, LOGGING_FORMAT, ColorFormatter, get_token

TOKEN = get_token()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def config_logging() -> None:
    """
    Config logging settings using command-line arguments.

    CLI args are:
    --logfile {str}
    --nostreamlogging {store_true}

    Defaults are:
    --logfile logs.log
    """

    parser = argparse.ArgumentParser(
        description="Run CatBot with optional logging arguments"
    )
    parser.add_argument(
        "--logfile",
        type=str,
        help="Path to the file where logs will be written, defaults to 'logs.log'",
    )
    parser.add_argument(
        "--nostreamlogging", action="store_true", help="Disable console logging"
    )

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


@bot.event
async def on_ready() -> None:
    """
    Sync and register slash commands.
    """

    await bot.tree.sync()
    await bot.change_presence(activity=discord.Game(name="/help"))
    logging.info("Logged in as %s and slash commands synced", bot.user.name)  # type: ignore


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    """
    Command error handler.

    :param interaction: Interaction instance
    :type interaction: discord.Interaction
    :param error: Error that occurred
    :type error: app_commands.AppCommandError
    """

    if isinstance(error, app_commands.errors.CheckFailure):  # Restricted command
        logging.info(
            "Unauthorized user %s attempted to use a restricted command",
            interaction.user,
        )
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
    elif isinstance(error, discord.Forbidden):
        logging.warning(
            "Attempted to perform a command with inadequate permissions allotted to the bot"
        )
        await interaction.response.send_message(
            "I do not have permissions to perform this command.", ephemeral=True
        )
    else:
        logging.error("An error occurred: %s", error, exc_info=True)
        await interaction.response.send_message(
            "An unknown error occurred. Contact @zentiph to report this please!",
            ephemeral=True,
        )


async def setup() -> None:
    """
    Load necessary cogs.
    """

    await bot.load_extension("CatBot.color.color_roles")
    await bot.load_extension("CatBot.color.color_tools")


async def main() -> None:
    """
    Main entrypoint.
    """

    with open(LOG_FILE, "w", encoding="utf8"):
        logging.info("Log file %s cleared", LOG_FILE)

    await setup()
    await bot.start(TOKEN)


if __name__ == "__main__":
    config_logging()
    run(main())
