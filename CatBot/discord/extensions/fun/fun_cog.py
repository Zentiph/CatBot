"""Fun commands."""

import secrets

import discord
from discord import app_commands
from discord.ext import commands
from psutil import Process

from ....pawprints import cog_setup_log_msg, log_app_command
from ...info import (
    DEPENDENCIES,
    DISCORD_DOT_PY_VERSION,
    HOST,
    PYTHON_VERSION,
    VERSION,
    get_uptime,
)
from ...interaction import (
    generate_response_embed,
    get_guild_interaction_data,
    report,
    safe_send,
)
from ...ui import COIN_HEADS_COLOR, COIN_TAILS_COLOR
from ...ui.emoji import Status, Visual


async def _ensure_full_user(
    client: discord.Client, user: discord.abc.User
) -> discord.User:
    return await client.fetch_user(user.id)


class FunCog(commands.Cog, name="Fun Commands"):
    """Cog containing fun commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create the FunCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(name="stats", description="Get stats about CatBot")
    async def stats(self, interaction: discord.Interaction) -> None:
        """Report stats about CatBot."""
        log_app_command(interaction)

        await interaction.response.defer(thinking=True)

        guilds = str(len(self.bot.guilds))
        memory_mb = Process().memory_info().rss / (1024**2)

        embed, icon = generate_response_embed(
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

    @app_commands.command(name="coinflip", description="Flip a coin (50/50 odds)")
    async def coin_flip(self, interaction: discord.Interaction) -> None:
        """Flip a coin, returning an embed with custom coin images."""
        log_app_command(interaction)

        title = f"{Visual.COIN} Coin Flip"
        description = "Here's the result of your coin flip."

        heads = secrets.randbelow(2)  # 0 or 1
        if heads:
            embed, icon = generate_response_embed(
                title=title, description=description, color=COIN_HEADS_COLOR
            )
            coin = discord.File(fp="CatBot/images/coin_heads.png", filename="coin.png")
        else:
            embed, icon = generate_response_embed(
                title=title, description=description, color=COIN_TAILS_COLOR
            )
            coin = discord.File(fp="CatBot/images/coin_tails.png", filename="coin.png")

        embed.set_image(url="attachment://coin.png")

        await safe_send(interaction, embed=embed, files=(coin, icon))

    @app_commands.command(name="profile", description="Get a user's profile picture")
    @app_commands.describe(user="User to get the profile picture of")
    async def profile(
        self, interaction: discord.Interaction, user: discord.abc.User | None = None
    ) -> None:
        """Get a user's profile picture."""
        log_app_command(interaction)

        interaction_user = interaction.user
        target = user or interaction_user
        display_name = target.display_name

        embed, icon = generate_response_embed(
            title=f"{Visual.PHOTO} {display_name}'s Profile Picture",
            description=f"Here's {display_name}'s profile picture.",
        )
        embed.set_image(url=target.display_avatar.url)

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.command(name="banner", description="Get a user's profile banner")
    @app_commands.describe(user="User to get the profile banner of")
    async def banner(
        self, interaction: discord.Interaction, user: discord.abc.User | None = None
    ) -> None:
        """Get a user's profile banner."""
        log_app_command(interaction)

        target = user or interaction.user
        # get the full user payload to ensure it has the banner info
        full_user = await _ensure_full_user(interaction.client, target)

        if full_user.banner is None:
            await report(
                interaction,
                f"{full_user.display_name} does not have a banner.",
                Status.FAILURE,
            )
            return

        display_name = full_user.display_name

        embed, icon = generate_response_embed(
            title=f"{Visual.PHOTO} {display_name}'s Profile Banner",
            description=f"Here's {display_name}'s profile banner.",
        )
        embed.set_image(url=full_user.banner.url)

        await interaction.response.send_message(embed=embed, file=icon)

    # TODO: add more to /cat-pic, maybe /animal {animal} instead and add more APIs?

    @app_commands.command(
        name="members", description="Get data regarding the members in this server"
    )
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

        embed, icon = generate_response_embed(
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
            inline=False,
        )
        embed.add_field(name="Online Members", value=online_members, inline=False)
        embed.add_field(
            name="Offline Members",
            value=member_count - online_members,
            inline=False,
        )

        await interaction.response.send_message(embed=embed, file=icon)
