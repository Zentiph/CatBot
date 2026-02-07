"""DB settings storage."""

from datetime import UTC, datetime
from typing import Any, TypedDict

import aiosqlite

from .db import DB_DIR

__author__ = "Gavin Borne"
__license__ = "MIT"


class GuildSettings(TypedDict):
    """Settings for a guild."""

    locale: str
    log_channel_id: int
    config_json: dict[str, Any]


_DB_FILENAME = "bot.sqlite"

_SCHEMA = """--sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id        TEXT PRIMARY KEY,
    locale          TEXT,
    log_channel_id  TEXT,
    config_json     TEXT,
    updated_at      TEXT NOT NULL
);
"""


class SettingsStore:
    """A DB manager for storing guild and user settings."""

    def __init__(self) -> None:
        """A DB manager for storing guild and user settings."""
        self.__conn: aiosqlite.Connection | None = None

    async def connect(self) -> aiosqlite.Connection:
        """Create or return a cached SQLite connection.

        Returns:
            aiosqlite.Connection: The active connection instance.
        """
        if self.__conn is None:
            self.__conn = await aiosqlite.connect(DB_DIR / _DB_FILENAME)
            await self.__conn.executescript(_SCHEMA)
            await self.__conn.commit()
        return self.__conn

    async def set_guild_settings(
        self,
        guild_id: int,
        *,
        locale: str | None = None,
        log_channel_id: int | None = None,
        config_json: str | None = None,
    ) -> None:
        """Upsert settings for a guild.

        Args:
            guild_id (int): The guild ID to update.
            locale (str | None): Optional locale string.
            log_channel_id (int | None): Optional log channel ID.
            config_json (str | None): Optional JSON-serialized settings blob.
        """
        conn = await self.connect()
        now = datetime.now(UTC).isoformat()
        await conn.execute(
            """--sql
            INSERT INTO guild_settings (
                guild_id, prefix, locale, log_channel_id, config_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                prefix = excluded.prefix,
                locale = excluded.locale,
                log_channel_id = excluded.log_channel_id,
                config_json = excluded.config_json,
                updated_at = excluded.updated_at;
            """,
            (
                str(guild_id),
                locale,
                str(log_channel_id) if log_channel_id else None,
                config_json,
                now,
            ),
        )

    async def get_guild_settings(self, guild_id: int) -> GuildSettings | None:
        """Fetch settings for a guild.

        Args:
            guild_id (int): The guild ID to fetch.

        Returns:
            GuildSettings | None: The settings if present, otherwise None.
        """
        conn = await self.connect()
        async with conn.execute(
            """--sql
            SELECT locale, log_channel_id, config_json
            FROM guild_settings WHERE guild_id = ?;
            """,
            (str(guild_id),),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            return None
        return {
            "locale": row[0],
            "log_channel_id": int(row[1]),
            "config_json": row[2],
        }


settings_store = SettingsStore()
