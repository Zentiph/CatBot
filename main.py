"""
main.py
Main file.
"""

import logging
from asyncio import run
from requests.exceptions import Timeout

import discord
from discord import app_commands

from CatBot.bot_init import (
    LOG_FILE,
    config_logging,
    get_token,
    initialize_bot,
    initialize_cli_arg_parser,
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
        logging.warning(
            "The application has been started in testing mode; ignore if this is intentional"
        )
    else:
        await bot.change_presence(activity=discord.Game(name="/help"))

    logging.info("Logged in as %s and slash commands synced", bot.user.name)  # type: ignore
    logging.info("---------------------------------------------")


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
        try:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "You do not have permission to use this command.", ephemeral=True
            )
    elif isinstance(error, discord.Forbidden):
        logging.warning(
            "Attempted to perform a command with inadequate permissions allotted to the bot"
        )
        try:
            await interaction.response.send_message(
                "I do not have permissions to perform this command.", ephemeral=True
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "I do not have permissions to perform this command.", ephemeral=True
            )
    elif isinstance(error, OverflowError):
        logging.info("Overflow error occurred during a calculation")
        try:
            await interaction.response.send_message(
                "This calculation caused an arithmetic overflow. Try using smaller numbers.",
                ephemeral=True,
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "This calculation caused an arithmetic overflow. Try using smaller numbers.",
                ephemeral=True,
            )
    elif isinstance(error, Timeout):
        logging.warning("Timeout error occurred during HTTP request")
        try:
            await interaction.response.send_message(
                "An attempt to communicate with an external API has taken too long, and has been canceled.",
                ephemeral=True,
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "An attempt to communicate with an external API has taken too long, and has been canceled.",
                ephemeral=True,
            )
    else:
        logging.error("An error occurred: %s", error)
        try:
            await interaction.response.send_message(
                "An unknown error occurred. Contact @zentiph to report this please!",
                ephemeral=True,
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "An unknown error occurred. Contact @zentiph to report this please!",
                ephemeral=True,
            )


async def setup() -> None:
    """
    Reset logs and load necessary cogs.
    """

    with open(LOG_FILE, "w", encoding="utf8"):
        logging.info("Log file %s cleared", LOG_FILE)

    if cli_args.testing:
        await bot.load_extension("CatBot.experiments.experimental")

    await bot.load_extension("CatBot.color.color")
    await bot.load_extension("CatBot.date_time.date_time")
    await bot.load_extension("CatBot.fun.fun")
    await bot.load_extension("CatBot.help.help")
    await bot.load_extension("CatBot.management.management")
    await bot.load_extension("CatBot.management.moderation")
    await bot.load_extension("CatBot.math.maths")
    await bot.load_extension("CatBot.rand.rand")


def main():
    """
    Config logging, run setup, and run the bot.
    """

    config_logging(parser)
    run(setup())
    bot.run(get_token(parser))


if __name__ == "__main__":
    main()
