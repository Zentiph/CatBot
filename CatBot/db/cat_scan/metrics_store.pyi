from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Final

import aiosqlite

__author__: Final[str]
__license__: Final[str]

@dataclass
class YearlyMetricStore:
    root: Path = Path("data") / "meow_metrics"
    _connections: dict[int, aiosqlite.Connection] = field(default_factory=dict)

    async def get_connection(self, year: int, /) -> aiosqlite.Connection: ...
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
        word_count: int,
        char_count: int,
        attachment_count: int,
        image_count: int,
        video_count: int,
        sticker_count: int,
        embed_count: int,
    ) -> None: ...
    async def commit(self, year: int, /) -> None: ...
    async def get_latest_timestamp(
        self, year: int, /, channel_id: int
    ) -> datetime | None: ...
