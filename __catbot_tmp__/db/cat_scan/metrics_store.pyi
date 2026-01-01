from datetime import datetime
from pathlib import Path
from typing import Final

import aiosqlite

__author__: Final[str]
__license__: Final[str]

DATA_ROOT_DIR: Final[Path]

class YearlyMetricStore:
    def __init__(self) -> None: ...
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

metric_store: Final[YearlyMetricStore]
