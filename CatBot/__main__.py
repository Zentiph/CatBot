"""
main.py
Main file.
"""

from asyncio import run

import discord

from .CatBot_utils import (
    LOG_FILE,
    config_logging,
    get_token,
    handle_app_command_error,
    initialize_bot,
    initialize_cli_arg_parser,
    pawprints,
)

bot = initialize_bot()
parser = initialize_cli_arg_parser()
cli_args = parser.parse_args()


@bot.event
async def on_ready() -> None:
    """
    Sync and register slash commands.
    """

    await bot.tree.sync()

    if cli_args.testing:
        await bot.change_presence(activity=discord.Game(name="⚠ TESTING ⚠"))
        pawprints.warning(
            "The application has been started in testing mode; ignore if this is intentional"
        )
    else:
        await bot.change_presence(activity=discord.Game(name="/help"))

    pawprints.setup(f"Logged in as {bot.user.name} and slash commands synced")  # type: ignore
    pawprints.setup("---------------------------------------------")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: Exception
) -> None:
    """
    Command error handler.

    :param interaction: Interaction instance
    :type interaction: discord.Interaction
    :param error: Error that occurred
    :type error: Exception
    """

    await handle_app_command_error(interaction, error)


async def setup() -> None:
    """
    Reset logs and load necessary cogs.
    """

    with open(LOG_FILE, "w", encoding="utf8"):
        pawprints.setup(f"Log file {LOG_FILE} cleared")

    if cli_args.testing:
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
    Config logging, run setup, and run the bot.
    """

    config_logging(parser)
    run(setup())
    bot.run(get_token(parser))


main()
