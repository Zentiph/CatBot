from datetime import UTC, datetime
from pathlib import Path

import pytest

from fizzbuzz.db.wrapped.metrics_store import MetricStoreConfig, YearlyMetricStore


@pytest.fixture
def store(tmp_path: Path) -> YearlyMetricStore:
    # store inside pytest temp dir
    cfg = MetricStoreConfig(data_root_dir=tmp_path / "data" / "wrapped")
    return YearlyMetricStore(config=cfg)


@pytest.mark.asyncio
async def test_get_connection_creates_db_and_schema(store: YearlyMetricStore) -> None:
    year = 2026
    conn = await store.get_connection(year)

    # DB file exists
    db_path = store.db_path(year)
    assert db_path.exists()

    # table exists
    async with conn.execute(
        """--sql
        SELECT name FROM sqlite_master WHERE type='table' AND name='messages';
        """
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None
    assert row[0] == "messages"

    # indices exist
    async with conn.execute(
        """--sql
        SELECT name FROM sqlite_master
            WHERE type='index' AND name='idx_messages_channel_date';
        """
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None
    assert row[0] == "idx_messages_channel_date"

    await store.close()


@pytest.mark.asyncio
async def test_get_connection_is_cached(store: YearlyMetricStore) -> None:
    year = 2026

    conn1 = await store.get_connection(year)
    conn2 = await store.get_connection(year)

    assert conn1 is conn2

    await store.close()


@pytest.mark.asyncio
async def test_insert_message_computes_word_and_char_count(  # noqa PLR0914 (too many locals)
    store: YearlyMetricStore,
) -> None:
    year = 2026

    content = "Hello, world!   Me"
    created_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC).isoformat()

    await store.insert_message(
        year,
        message_id=1,
        channel_id=10,
        author_id=20,
        created_at_iso=created_at,
        content=content,
        attachment_count=2,
        image_count=1,
        video_count=0,
        sticker_count=0,
        embed_count=3,
    )
    await store.commit(year)

    conn = await store.get_connection(year)
    async with conn.execute(
        """--sql
        SELECT
            message_id, channel_id, author_id, created_at, content,
            word_count, char_count,
            attachment_count, image_count, video_count, sticker_count, embed_count
        FROM messages
        WHERE message_id = ?;
        """,
        ("1",),
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None

    (
        message_id,
        channel_id,
        author_id,
        created_at_db,
        content_db,
        word_count,
        char_count,
        attachment_count,
        image_count,
        video_count,
        sticker_count,
        embed_count,
    ) = row

    assert message_id == "1"
    assert channel_id == "10"
    assert author_id == "20"
    assert created_at_db == created_at
    assert content_db == content

    assert word_count == 3
    assert char_count == len(content)

    assert attachment_count == 2
    assert image_count == 1
    assert video_count == 0
    assert sticker_count == 0
    assert embed_count == 3

    await store.close()


@pytest.mark.asyncio
async def test_inset_message_null_content_counts_zero(store: YearlyMetricStore) -> None:
    year = 2026
    created_at = datetime(2026, 2, 1, 0, 0, 0, tzinfo=UTC).isoformat()

    await store.insert_message(
        year,
        message_id=2,
        channel_id=10,
        author_id=20,
        created_at_iso=created_at,
        content=None,
        attachment_count=0,
        image_count=0,
        video_count=0,
        sticker_count=0,
        embed_count=0,
    )
    await store.commit(year)

    conn = await store.get_connection(year)
    async with conn.execute(
        """--sql
        SELECT word_count, char_count, content FROM messages WHERE message_id = ?;
        """,
        ("2",),
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None
    assert row == (0, 0, None)

    await store.close()


@pytest.mark.asyncio
async def test_insert_message_replaces_same_message_id(
    store: YearlyMetricStore,
) -> None:
    year = 2026

    created_at1 = datetime(2026, 3, 1, 0, 0, 0, tzinfo=UTC).isoformat()
    created_at2 = datetime(2026, 3, 2, 0, 0, 0, tzinfo=UTC).isoformat()

    await store.insert_message(
        year,
        message_id=3,
        channel_id=10,
        author_id=20,
        created_at_iso=created_at1,
        content="first",
        attachment_count=0,
        image_count=0,
        video_count=0,
        sticker_count=0,
        embed_count=0,
    )
    await store.insert_message(
        year,
        message_id=3,  # same PK -> replace
        channel_id=10,
        author_id=20,
        created_at_iso=created_at2,
        content="second message",
        attachment_count=1,
        image_count=0,
        video_count=1,
        sticker_count=0,
        embed_count=0,
    )
    await store.commit(year)

    conn = await store.get_connection(year)
    async with conn.execute(
        """--sql
        SELECT
            created_at, content, word_count, char_count, attachment_count, video_count
        FROM messages
        WHERE message_id = ?;
        """,
        ("3",),
    ) as cur:
        row = await cur.fetchone()

    assert row is not None
    created_at_db, content_db, word_count, char_count, attachment_count, video_count = (
        row
    )

    assert created_at_db == created_at2
    assert content_db == "second message"
    assert word_count == 2
    assert char_count == len("second message")
    assert attachment_count == 1
    assert video_count == 1

    async with conn.execute(
        "SELECT COUNT(*) FROM messages WHERE message_id = ?;",
        ("3",),
    ) as cur:
        count_row = await cur.fetchone()
    assert count_row is not None
    assert count_row[0] == 1

    await store.close()


@pytest.mark.asyncio
async def test_get_latest_timestamp_none_when_empty(store: YearlyMetricStore) -> None:
    year = 2026

    latest = await store.get_latest_timestamp(year, channel_id=999)
    assert latest is None

    await store.close()


@pytest.mark.asyncio
async def test_get_latest_timestamp_returns_max_for_channel(
    store: YearlyMetricStore,
) -> None:
    year = 2026
    channel_id = 10

    t1 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC).isoformat()
    t2 = datetime(2026, 1, 5, 12, 30, 0, tzinfo=UTC).isoformat()
    t_other = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC).isoformat()

    await store.insert_message(
        year,
        message_id=10,
        channel_id=channel_id,
        author_id=1,
        created_at_iso=t1,
        content="a",
        attachment_count=0,
        image_count=0,
        video_count=0,
        sticker_count=0,
        embed_count=0,
    )
    await store.insert_message(
        year,
        message_id=11,
        channel_id=channel_id,
        author_id=1,
        created_at_iso=t2,
        content="b",
        attachment_count=0,
        image_count=0,
        video_count=0,
        sticker_count=0,
        embed_count=0,
    )
    await store.insert_message(
        year,
        message_id=12,
        channel_id=999,  # should not affect channel_id
        author_id=1,
        created_at_iso=t_other,
        content="c",
        attachment_count=0,
        image_count=0,
        video_count=0,
        sticker_count=0,
        embed_count=0,
    )
    await store.commit(year)

    latest = await store.get_latest_timestamp(year, channel_id=channel_id)
    assert latest == datetime.fromisoformat(t2)

    await store.close()
