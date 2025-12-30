"""Log metrics for the Cat Scan event."""

from datetime import UTC, datetime
from logging import getLogger

import discord
from discord.ext import commands

from ....db.cat_scan import metric_store
from ...info import CAT_GUILD_ID

COMMIT_EVERY = 512

FIRST_YEAR = 2025
CUTOFF_MONTH = 12
CUTOFF_DAY = 15

IGNORED_CHANNELS: set[int] = set()
IGNORED_CATEGORIES = {
    990458499387518976,  # info
    1050538201946800158,  # archived
    990449082604589136,  # admin
}


logger = getLogger(__name__)


class CatScanLoggerCog(commands.Cog):
    """Logs messages for Cat Scan and backfills missed ones on startup."""

    def __init__(self, bot: commands.Bot) -> None:
        """Logs messages for Cat Scan and backfills missed ones on startup.

        Args:
            bot (commands.Bot): The bot to add the cog to.
        """
        self.bot = bot
        self._catchup_started = False

    def _get_year_and_cutoff(self, created_at: datetime, /) -> tuple[int, datetime]:
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        else:
            created_at = created_at.astimezone(UTC)

        year = created_at.year
        cutoff = datetime(year, CUTOFF_MONTH, CUTOFF_DAY, 23, 59, 59, tzinfo=UTC)
        return year, cutoff

    def _should_ignore(self, message: discord.Message) -> bool:
        channel = message.channel
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return True  # ignore DMs/voice/etc

        if channel.id in IGNORED_CHANNELS:
            return True

        category = channel.category
        return category is not None and category.id in IGNORED_CATEGORIES

    async def _log_single_message(
        self, message: discord.Message, *, commit: bool
    ) -> None:
        if (
            message.guild is None
            or message.author.bot
            or message.guild.id != CAT_GUILD_ID
            or self._should_ignore(message)
        ):
            return

        created = message.created_at
        year, cutoff = self._get_year_and_cutoff(created)

        if year < FIRST_YEAR:
            return

        created_utc = (
            created.replace(tzinfo=UTC)
            if created.tzinfo is None
            else created.astimezone(UTC)
        )
        if created_utc > cutoff:
            return

        content = message.content or ""

        attachments = message.attachments
        attachment_count = len(attachments)

        image_count = video_count = 0
        for attachment in attachments:
            content_type = attachment.content_type or ""
            filename = attachment.filename.lower()
            if any(
                (
                    content_type.startswith("image/"),
                    filename.endswith(".png"),
                    filename.endswith(".jpg"),
                    filename.endswith(".jpeg"),
                    filename.endswith(".gif"),
                    filename.endswith(".webp"),
                )
            ):
                image_count += 1
            if any(
                (
                    content_type.startswith("video/"),
                    filename.endswith(".mp4"),
                    filename.endswith(".mov"),
                )
            ):
                video_count += 1

        sticker_count = len(message.stickers)
        embed_count = len(message.embeds)

        created_iso = created_utc.isoformat()

        await metric_store.insert_message(
            year,
            message_id=message.id,
            channel_id=message.channel.id,
            author_id=message.author.id,
            created_at_iso=created_iso,
            content=content,
            attachment_count=attachment_count,
            image_count=image_count,
            video_count=video_count,
            sticker_count=sticker_count,
            embed_count=embed_count,
        )

        if commit:
            await metric_store.commit(year)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Log messages as they come in."""
        try:
            await self._log_single_message(message, commit=True)
        except Exception:
            logger.exception("Failed to log message for Cat Scan")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Catch up on missed messages on startup."""
        if self._catchup_started:
            return
        self._catchup_started = True

        self.bot.loop.create_task(self._run_catchup())

    async def _run_catchup(self) -> None:
        await self.bot.wait_until_ready()

        now_utc = datetime.now(UTC)
        current_year = now_utc.year
        if current_year < FIRST_YEAR:
            logger.info(
                "Cat Scan catchup: current year is before FIRST_YEAR, skipping."
            )
            return

        _, cutoff = self._get_year_and_cutoff(now_utc)
        window_end = min(now_utc, cutoff)
        start_of_year = datetime(current_year, 1, 1, tzinfo=UTC)

        logger.info(
            "Cat Scan catchup: year=%s, window %s -> %s",
            current_year,
            start_of_year.isoformat(),
            window_end.isoformat(),
        )

        guild = next((g for g in self.bot.guilds if g.id == CAT_GUILD_ID), None)
        if guild is None:
            logger.error(
                "CatBot is not in the cat server! "
                "Ensure the CAT_GUILD_ID is set correctly in info.py"
            )
            return

        text_channels = [
            c
            for c in guild.text_channels
            if c.permissions_for(guild.me).read_message_history
        ]

        for channel in text_channels:
            try:
                await self._catchup_channel(
                    channel,
                    year=current_year,
                    start_of_year=start_of_year,
                    window_end=window_end,
                )
            except Exception:
                logger.exception(
                    "Cat Scan: failed on channel #%s (%s)", channel.name, channel.id
                )

        logger.info("Cat Scan catchup: finished.")

    async def _catchup_channel(
        self,
        channel: discord.TextChannel,
        *,
        year: int,
        start_of_year: datetime,
        window_end: datetime,
    ) -> None:
        latest = await metric_store.get_latest_timestamp(year, channel_id=channel.id)
        after = latest if latest is not None else start_of_year

        if latest is not None and latest >= window_end:
            # already caught up
            return

        logger.info(
            "Cat Scan: #%s (%s) after=%s before=%s",
            channel.name,
            channel.id,
            after.isoformat(),
            window_end.isoformat(),
        )

        batch = 0
        async for message in channel.history(
            limit=None, oldest_first=True, after=after, before=window_end
        ):
            try:
                await self._log_single_message(message, commit=False)
            except Exception:
                logger.exception(
                    "Cat Scan catchup: failed logging message %s in #%s",
                    message.id,
                    channel.name,
                )

            batch += 1
            if batch >= COMMIT_EVERY:
                await metric_store.commit(year)
                batch = 0

        if batch > 0:  # flush at the end
            await metric_store.commit(year)


async def setup(bot: commands.Bot) -> None:
    """Load the CatScanLogger cog."""
    await bot.add_cog(CatScanLoggerCog(bot))
