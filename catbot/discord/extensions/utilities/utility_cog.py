"""Utility commands."""

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from psutil import Process

from ....util.pawprints import cog_setup_log_msg, log_app_command
from ...info import (
    DEPENDENCIES,
    DISCORD_DOT_PY_VERSION,
    HOST,
    PYTHON_VERSION,
    VERSION,
    get_uptime,
)
from ...interaction import (
    build_response_embed,
    get_guild_interaction_data,
    report,
    safe_send,
)
from ...ui.emoji import Status, Visual
from ..help import help_info

__author__ = "Gavin Borne"
__license__ = "MIT"

# I love making Ruff happy.....
_DATE_TH_SUFFIX_EXCEPTION_RANGE_MIN = 11
_DATE_TH_SUFFIX_EXCEPTION_RANGE_MAX = 13


def _ordinal(n: int, /) -> str:
    if (
        _DATE_TH_SUFFIX_EXCEPTION_RANGE_MIN
        <= n % 100
        <= _DATE_TH_SUFFIX_EXCEPTION_RANGE_MAX
    ):
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _human_date(dt: datetime, /) -> str:
    return f"{dt.day}{_ordinal(dt.day)} {dt.strftime('%B %Y')}"


class UtilityCog(commands.Cog, name="Utility Commands"):
    """Cog containing utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create the UtilityCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(name="stats", description="Get stats about CatBot")
    @help_info("Utilities")
    async def stats(self, interaction: discord.Interaction) -> None:
        """Report stats about CatBot."""
        log_app_command(interaction)

        await interaction.response.defer(thinking=True)

        guilds = str(len(self.bot.guilds))
        memory_mb = Process().memory_info().rss / (1024**2)

        embed, icon = build_response_embed(
            title=f"{Visual.CHART} CatBot Stats",
            description="Here's some statistics about myself.",
        )
        embed.add_field(name="Version", value=VERSION)
        embed.add_field(name="# of Guilds", value=guilds)
        embed.add_field(
            name="Uptime",
            value=get_uptime(),
            inline=False,
        )
        embed.add_field(name="Language", value=f"Python {PYTHON_VERSION}")
        embed.add_field(name="Memory Usage", value=f"{memory_mb:.2f} MB")
        embed.add_field(name="Package", value=f"discord.py {DISCORD_DOT_PY_VERSION}")
        embed.add_field(name="Dependencies", value=DEPENDENCIES)
        embed.add_field(name="Host", value=HOST, inline=False)

        await safe_send(interaction, embed=embed, file=icon)

    @app_commands.command(name="server", description="Get info about this server")
    @help_info("Utilities")
    async def server(self, interaction: discord.Interaction) -> None:
        """Get server info."""
        log_app_command(interaction)

        data = get_guild_interaction_data(interaction)
        if data is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        guild = data.guild

        owner = guild.owner
        guild_icon = guild.icon

        embed, icon = build_response_embed(
            title=f"{Visual.COMPUTER} {guild.name} Information",
            description=(
                "Here's some information about this server.\n"
                "(For member info, use `/members`)."
            ),
        )
        if guild_icon is not None:
            embed.set_image(url=guild_icon.url)

        if owner is not None:
            embed.add_field(name="Owner", value=owner.mention)
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Creation Date", value=_human_date(guild.created_at))

        embed.add_field(
            name="# of Categories", value=len(guild.categories), inline=False
        )
        embed.add_field(name="# of Channels", value=len(guild.channels))
        embed.add_field(name="# of Text Channels", value=len(guild.text_channels))
        embed.add_field(name="# of Voice Channels", value=len(guild.voice_channels))

        embed.add_field(name="# of Roles", value=len(guild.roles), inline=False)
        embed.add_field(name="# of Emojis", value=len(guild.emojis))
        embed.add_field(name="# of Stickers", value=len(guild.stickers))

        await safe_send(interaction, embed=embed, file=icon)

    @app_commands.command(
        name="members", description="Get info about the members in this server"
    )
    @help_info("Utilities")
    async def members(self, interaction: discord.Interaction) -> None:
        """Get member info."""
        log_app_command(interaction)

        data = get_guild_interaction_data(interaction)
        if data is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        guild = data.guild
        members = guild.members
        member_count = guild.member_count
        if member_count is None:
            await report(
                interaction,
                "Could not fetch member info, please try again later.",
                Status.WARNING,
            )
            return

        human_members = len([member for member in members if not member.bot])
        online_members = len(
            [member for member in members if str(member.status) != "offline"]
        )

        embed, icon = build_response_embed(
            title=f"{Visual.PEOPLE_SYMBOL} {guild.name} Member Count",
            description="Here's the member count for this server.",
        )
        embed.add_field(
            name="Total Members",
            value=member_count,
            inline=False,
        )
        embed.add_field(name="Human Members", value=human_members, inline=False)
        embed.add_field(
            name="Bot Members",
            value=member_count - human_members,
        )
        embed.add_field(name="Online Members", value=online_members, inline=False)
        embed.add_field(
            name="Offline Members",
            value=member_count - online_members,
        )

        await safe_send(interaction, embed=embed, file=icon)


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(UtilityCog(bot))
