"""
help.py
Help cog for CatBot.
"""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from ..internal import DEFAULT_EMBED_COLOR, generate_image_file
from .commands import (
    COLOR_ROLES,
    COLOR_TOOLS,
    HELP,
    MODERATION,
    PRIVATE,
    PRIVATE_COMMAND_MAP,
    PUBLIC,
    PUBLIC_COMMAND_MAP,
    ClassifiedHelpCategory,
    HelpCategory,
)
from .representations import generate_field_description, generate_field_title


class HelpCog(commands.Cog, name="Help Commands"):
    """
    Cog containing help commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("HelpCog loaded")

    help_group = app_commands.Group(
        name="help", description="Get help for using the bot"
    )

    @help_group.command(
        name="category", description="List all the commands in a category"
    )
    @app_commands.describe(category="Category of commands to get help for")
    async def help_category(
        self,
        interaction: discord.Interaction,
        category: HelpCategory,
    ) -> None:
        """
        Get help for `category`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param category: Category to get help for
        :type category: HelpCategory
        """

        logging.info(
            "/help category category=%s invoked by %s", category, interaction.user
        )

        match category:
            case "color roles":
                embed = discord.Embed(
                    title="Color Roles Commands Help Page",
                    description="Here's a list of color roles commands and how to use them.",
                    color=DEFAULT_EMBED_COLOR,
                )
                icon = generate_image_file("CatBot/images/profile.jpg")
                embed.set_author(name="CatBot", icon_url="attachment://image.png")

                for command in COLOR_ROLES:
                    embed.add_field(
                        name=generate_field_title(command),
                        value=generate_field_description(command),
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed, file=icon)

            case "color tools":
                embed = discord.Embed(
                    title="Color Tools Commands Help Page",
                    description="Here's a list of color tools commands and how to use them.",
                    color=DEFAULT_EMBED_COLOR,
                )
                icon = generate_image_file("CatBot/images/profile.jpg")
                embed.set_author(name="CatBot", icon_url="attachment://image.png")

                for command in COLOR_TOOLS:
                    embed.add_field(
                        name=generate_field_title(command),
                        value=generate_field_description(command),
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed, file=icon)

            case "help":
                embed = discord.Embed(
                    title="Help Commands Help Page",
                    description="...Seriously? Okay then.",
                    color=DEFAULT_EMBED_COLOR,
                )
                icon = generate_image_file("CatBot/images/profile.jpg")
                embed.set_author(name="CatBot", icon_url="attachment://image.png")

                for command in HELP:
                    embed.add_field(
                        name=generate_field_title(command),
                        value=generate_field_description(command),
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed, file=icon)

            case _:
                await interaction.response.send_message(
                    "You have entered an incorrect category.", ephemeral=True
                )
                # This shouldn't be possible
                logging.error(
                    "/help category category=%s was not stopped by Discord type-checking",
                    category,
                )

    @help_group.command(
        name="command", description="Get help regarding a specific command"
    )
    @app_commands.describe(cmd="Command to get help for")
    async def help_command(self, interaction: discord.Interaction, cmd: str) -> None:
        """
        Get help for `cmd`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param cmd: Command to get help for
        :type cmd: str
        """

        logging.info("/help command cmd=%s invoked by %s", cmd, interaction.user)

        if cmd not in (command.name for command in PUBLIC) and cmd not in (
            f"{command.group} {command.name}" for command in PUBLIC
        ):
            await interaction.response.send_message(
                f"I do not have a public command called **{cmd}**!", ephemeral=True
            )
            return

        command = PUBLIC_COMMAND_MAP[cmd]
        embed = discord.Embed(
            title=f"{cmd} Help Page",
            description=f"Here's how to use **{cmd}**.",
            color=DEFAULT_EMBED_COLOR,
        )
        icon = generate_image_file("CatBot/images/profile.jpg")
        embed.set_author(name="CatBot", icon_url="attachment://image.png")

        embed.add_field(
            name=generate_field_title(command),
            value=generate_field_description(command),
        )

        await interaction.response.send_message(embed=embed, file=icon)


class ClassifiedHelpCog(commands.Cog, name="Moderation Help Commands"):
    """
    Cog containing moderator-only help commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Run when the cog is ready to be used.
        """

        logging.info("ClassifiedHelpCog loaded")

    help_group = app_commands.Group(
        name="help-mod", description="Get help for using the bot's moderation commands"
    )

    @help_group.command(
        name="category", description="List all the commands in a category"
    )
    @app_commands.describe(category="Category of commands to get help for")
    async def help_category(
        self,
        interaction: discord.Interaction,
        category: ClassifiedHelpCategory,
    ) -> None:
        """
        Get help for `category`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param category: Category to get help for
        :type category: ClassifiedHelpCategory
        """

        logging.info(
            "/help-mod category category=%s invoked by %s", category, interaction.user
        )

        match category:
            case "moderation":
                embed = discord.Embed(
                    title="Moderation Commands Help Page",
                    description="Here's a list of moderation commands and how to use them.",
                    color=DEFAULT_EMBED_COLOR,
                )
                icon = generate_image_file("CatBot/images/profile.jpg")
                embed.set_author(name="CatBot", icon_url="attachment://image.png")

                for command in MODERATION:
                    embed.add_field(
                        name=generate_field_title(command),
                        value=generate_field_description(command),
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed, file=icon)

            case _:
                await interaction.response.send_message(
                    "You have entered an incorrect category.", ephemeral=True
                )
                # This shouldn't be possible
                logging.error(
                    "/help-mod category category=%s was not stopped by Discord type-checking",
                    category,
                )

    @help_group.command(
        name="command", description="Get help regarding a specific command"
    )
    @app_commands.describe(cmd="Command to get help for")
    async def help_command(self, interaction: discord.Interaction, cmd: str) -> None:
        """
        Get help for `cmd`.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param cmd: Command to get help for
        :type cmd: str
        """

        logging.info("/help-mod command cmd=%s invoked by %s", cmd, interaction.user)

        if cmd not in (command.name for command in PRIVATE) and cmd not in (
            f"{command.group} {command.name}" for command in PRIVATE
        ):
            await interaction.response.send_message(
                f"I do not have a private command called **{cmd}**!", ephemeral=True
            )
            return

        command = PRIVATE_COMMAND_MAP[cmd]
        embed = discord.Embed(
            title=f"{cmd} Help Page",
            description=f"Here's how to use **{cmd}**.",
            color=DEFAULT_EMBED_COLOR,
        )
        icon = generate_image_file("CatBot/images/profile.jpg")
        embed.set_author(name="CatBot", icon_url="attachment://image.png")

        embed.add_field(
            name=generate_field_title(command),
            value=generate_field_description(command),
        )

        await interaction.response.send_message(embed=embed, file=icon)


async def setup(bot: commands.Bot):
    """
    Set up the HelpCog and ClassifiedHelpCog.

    :param bot: Bot to add the cog to.
    :type bot: commands.Bot
    """

    await bot.add_cog(HelpCog(bot))
    await bot.add_cog(ClassifiedHelpCog(bot))