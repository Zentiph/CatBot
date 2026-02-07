from typing import Any, Final, TypedDict

import aiosqlite

__author__: Final[str]
__license__: Final[str]

class GuildSettings(TypedDict):
    locale: str
    log_channel_id: int
    config_json: dict[str, Any]

class SettingsStore:
    def __init__(self) -> None: ...
    async def connect(self) -> aiosqlite.Connection: ...
    async def set_guild_settings(
        self,
        guild_id: int,
        *,
        locale: str | None = None,
        log_channel_id: int | None = None,
        config_json: str | None = None,
    ) -> None: ...
    async def get_guild_settings(self, guild_id: int) -> GuildSettings | None: ...

settings_store: Final[SettingsStore]
