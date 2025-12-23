"""Store message metrics for each year's Cat Scan event.

The event is similar to Spotify Wrapped, in which it compiles message data from
throughout the year which will then have statistics run on it to create a presentation
for the server.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import aiosqlite

__author__ = "Gavin Borne"
__license__ = "MIT"

_SCHEMA = """--sql
CREATE TABLE IF NOT EXISTS messages (
    message_id       TEXT PRIMARY KEY,
    channel_id       TEXT NOT NULL,
    author_id        TEXT NOT NULL,
    created_at       TEXT NOT NULL, -- ISO 8601 string
    content          TEXT,

    word_count       INTEGER NOT NULL,
    char_count       INTEGER NOT NULL,

    attachment_count INTEGER NOT NULL,
    image_count      INTEGER NOT NULL,
    video_count      INTEGER NOT NULL,
    sticker_count    INTEGER NOT NULL,
    embed_count      INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_author_date
    ON messages (author_id, created_at);

CREATE INDEX IF NOT EXISTS idx_messages_channel_date
    ON messages (channel_id, created_at);
"""


@dataclass
class YearlyMetricStore:
    """Manages one SQLite DB per year."""

    root: Path = Path("data") / "cat_scan"
    _connections: dict[int, aiosqlite.Connection] = field(default_factory=dict)

    async def get_connection(self, year: int, /) -> aiosqlite.Connection:
        """Get or create a DB connection for a given year.

        Args:
            year (int): The year to get the connection for.

        Returns:
            aiosqlite.Connection: The connection corresponding to the given year.
        """
        if year in self._connections:
            return self._connections[year]

        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"cat_scan_{year}.sqlite"

        connection = await aiosqlite.connect(path)
        await connection.execute("""--sql
                                 PRAGMA foreign_keys = ON;
                                 """)
        await connection.executescript(_SCHEMA)
        await connection.commit()

        self._connections[year] = connection
        return connection

    async def insert_message(
        self,
        year: int,
        /,
        *,
        message_id: int,
        channel_id: int,
        author_id: int,
        created_at_iso: str,
        content: str | None,
        attachment_count: int,
        image_count: int,
        video_count: int,
        sticker_count: int,
        embed_count: int,
    ) -> None:
        """Insert or replace a single message row for a given year.

        Args:
            year (int): The year.
            message_id (int): The ID of the sent message.
            channel_id (int): The ID of the channel the message was sent in.
            author_id (int): The ID of the message's author.
            created_at_iso (str): The ISO string for when the message was created.
            content (str | None): The content of the message.
            attachment_count (int): The number of attachments of the message.
            image_count (int): The number of images attached to the message.
            video_count (int): The number of videos attached to the message.
            sticker_count (int): The number of stickers attached to the message.
            embed_count (int): The number of embeds attached to the message.
        """
        connection = await self.get_connection(year)
        await connection.execute(
            """--sql
            INSERT OR REPLACE INTO messages (
                message_id,
                channel_id,
                author_id,
                created_at,
                content,
                word_count,
                char_count,
                attachment_count,
                image_count,
                video_count,
                sticker_count,
                embed_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                str(message_id),
                str(channel_id),
                str(author_id),
                created_at_iso,
                content,
                len(content.split()) if content else 0,  # word count
                len(content) if content else 0,  # char count
                attachment_count,
                image_count,
                video_count,
                sticker_count,
                embed_count,
            ),
        )

    async def commit(self, year: int, /) -> None:
        """Commit pending changes for a given year.

        Args:
            year (int): The year of the DB to commit to.
        """
        connection = await self.get_connection(year)
        await connection.commit()

    async def get_latest_timestamp(
        self, year: int, /, channel_id: int
    ) -> datetime | None:
        """Get the latest message timestamp that is stored.

        Args:
            year (int): The year to search in.
            channel_id (int): The channel to search in.

        Returns:
            datetime | None: The latest message timestamp,
                or None if there are none stored.
        """
        connection = await self.get_connection(year)
        async with connection.execute(
            """--sql
            SELECT MAX(created_at)
            FROM messages
            WHERE channel_id = ?;
            """,
            (str(channel_id),),
        ) as cursor:
            row = await cursor.fetchone()

        if not row or row[0] is None:
            return None

        return datetime.fromisoformat(row[0])
