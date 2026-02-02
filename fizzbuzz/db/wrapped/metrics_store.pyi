from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

import aiosqlite

__author__: Final[str]
__license__: Final[str]

ConnectFunction = Callable[[Path], Awaitable[aiosqlite.Connection]]

@dataclass(frozen=True, slots=True)
class MetricStoreConfig:
    data_root_dir: Path = ...
    schema_sql: str = ...

DEFAULT_METRIC_STORE_CONFIG: Final[MetricStoreConfig]

class YearlyMetricStore:
    def __init__(
        self,
        *,
        config: MetricStoreConfig = DEFAULT_METRIC_STORE_CONFIG,
        connect: ConnectFunction | None = None,
    ) -> None: ...
    def db_path(self, year: int, /) -> Path: ...
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
    async def close_year(self, year: int, /) -> None: ...
    async def close(self) -> None: ...

metric_store: Final[YearlyMetricStore]
