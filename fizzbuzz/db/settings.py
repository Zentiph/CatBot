"""DB settings storage."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Any, Literal

import aiosqlite

from .db import DB_DIR

__author__ = "Gavin Borne"
__license__ = "MIT"


_DB_FILENAME = "bot.sqlite"

_SCHEMA = """--sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS settings (
    scope       TEXT NOT NULL,  -- "guild", "user", "global"
    scope_id    TEXT NOT NULL,  -- guild_id/user_id or "global"
    key         TEXT NOT NULL,
    value_json  TEXT,
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (scope, scope_id, key)
);

CREATE INDEX IF NOT EXISTS idx_settings_scope
    ON settings (scope, scope_id);
"""

SettingsScope = Literal["guild", "user", "global"]


class SettingsManager:
    """A DB manager for general bot settings."""

    def __init__(self) -> None:
        """A DB manager for general bot settings."""
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

    def __dump_json(self, value: object) -> str:
        """Serialize a Python value to JSON.

        Args:
            value (object): The value to serialize.

        Returns:
            str: The JSON representation.
        """
        return json.dumps(value, ensure_ascii=True, separators=(",", ":"))

    def __load_json(self, value_json: str | None) -> object:
        """Deserialize JSON to a Python value.

        Args:
            value_json (str | None): The JSON string to parse.

        Returns:
            Any: The parsed value, or None if value_json is None.
        """
        if value_json is None:
            return None
        return json.loads(value_json)

    async def set_value(
        self,
        scope: SettingsScope,
        scope_id: int | str,
        key: str,
        value: object,
    ) -> None:
        """Insert or update a setting value.

        Args:
            scope (SettingsScope): The setting scope ("guild", "user", "global").
            scope_id (int | str): The scope identifier (guild/user id or "global").
            key (str): The setting key.
            value (object): The value to store (JSON-serializable).
        """
        conn = await self.connect()
        now = datetime.now(UTC).isoformat()
        value_json = self.__dump_json(value)
        await conn.execute(
            """--sql
            INSERT INTO settings (
                scope, scope_id, key, value_json, updated_at
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(scope, scope_id, key) DO UPDATE SET
                value_json = excluded.value_json,
                updated_at = excluded.updated_at;
            """,
            (
                scope,
                str(scope_id),
                key,
                value_json,
                now,
            ),
        )
        await conn.commit()

    async def get_value(
        self,
        scope: SettingsScope,
        scope_id: int | str,
        key: str,
    ) -> object | None:
        """Fetch a single setting value.

        Args:
            scope (SettingsScope): The setting scope.
            scope_id (int | str): The scope identifier.
            key (str): The setting key.

        Returns:
            object | None: The value if present, otherwise None.
        """
        conn = await self.connect()
        async with conn.execute(
            """--sql
            SELECT value_json
            FROM settings
            WHERE scope = ? AND scope_id = ? AND key = ?;
            """,
            (scope, str(scope_id), key),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            return None
        return self.__load_json(row[0])

    async def get_all(
        self, scope: SettingsScope, scope_id: int | str
    ) -> dict[str, Any]:
        """Fetch all settings for a scope.

        Args:
            scope (SettingsScope): The setting scope.
            scope_id (int | str): The scope identifier.

        Returns:
            dict[str, Any]: A mapping of setting keys to values.
        """
        conn = await self.connect()
        async with conn.execute(
            """--sql
            SELECT key, value_json
            FROM settings
            WHERE scope = ? AND scope_id = ?;
            """,
            (scope, str(scope_id)),
        ) as cursor:
            rows = await cursor.fetchall()
        return {row[0]: self.__load_json(row[1]) for row in rows}

    async def delete_value(
        self, scope: SettingsScope, scope_id: int | str, key: str
    ) -> None:
        """Delete a single setting value.

        Args:
            scope (SettingsScope): The setting scope.
            scope_id (int | str): The scope identifier.
            key (str): The setting key.
        """
        conn = await self.connect()
        await conn.execute(
            """
            DELETE FROM settings
            WHERE scope = ? AND scope_id = ? AND key = ?;
            """,
            (scope, str(scope_id), key),
        )
        await conn.commit()

    async def delete_scope(self, scope: SettingsScope, scope_id: int | str) -> None:
        """Delete all settings for a scope.

        Args:
            scope (SettingsScope): The setting scope.
            scope_id (int | str): The scope identifier.
        """
        conn = await self.connect()
        await conn.execute(
            """--sql
            DELETE FROM settings
            WHERE scope = ? AND scope_id = ?;
            """,
            (scope, str(scope_id)),
        )
        await conn.commit()


settings_manager = SettingsManager()
