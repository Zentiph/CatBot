"""Analyze the Cat Scan database to get stats."""

from argparse import ArgumentParser
from collections.abc import Iterable, Sequence
import contextlib
from pathlib import Path
import sqlite3
from typing import Any

__author__ = "Gavin Borne"
__license__ = "MIT"


class Reporter:
    """Writes outputs to both stdout and a log file."""

    def __init__(self, write_to: Path) -> None:
        """Writes outputs to both stdout and a log file.

        Args:
            write_to (Path): Where to write the report to.
        """
        self.__out_path = write_to
        self.__fp = write_to.open("w", encoding="utf-8")

    def close(self) -> None:
        """Close this Reporter, freeing its file pointer."""
        with contextlib.suppress(IOError):
            self.__fp.close()

    def write(self, text: str = "", /) -> None:
        """Write text to the report file and print it, with a newline appended.

        Args:
            text (str, optional): The text to write. Defaults to "".
        """
        print(text)
        self.__fp.write(text + "\n")

    def section(self, title: str, /) -> None:
        """Write a section header.

        Args:
            title (str): The title of the section.
        """
        line = "=" * (len(title) + 2)
        self.write()
        self.write(line)
        self.write(" " + title)
        self.write(line)

    def subsection(self, title: str, /) -> None:
        """Write a subsection header.

        Args:
            title (str): The title of the subsection.
        """
        line = "-" * len(title)
        self.write()
        self.write(title)
        self.write(line)


def query_all(
    connection: sqlite3.Connection, sql: str, params: Sequence[Any] | None = None
) -> list[tuple[Any, ...]]:
    """Query all the rows in the database with an SQL script and params.

    Args:
        connection (sqlite3.Connection): The connection to the DB to query.
        sql (str): The SQL script to run.
        params (Sequence[Any] | None, optional): The params to use. Defaults to None.

    Returns:
        list[tuple[Any, ...]]: The results of the query.
    """
    cursor = connection.cursor()
    cursor.execute(sql, params or [])
    rows = cursor.fetchall()
    cursor.close()
    return rows


def query_one(
    connection: sqlite3.Connection, sql: str, params: Sequence[Any] | None = None
) -> tuple[Any, ...] | None:
    """Query the database with an SQL script and params and return the first match.

    Args:
        connection (sqlite3.Connection): The connection to the DB to query.
        sql (str): The SQL script to run.
        params (Sequence[Any] | None, optional): The params to use. Defaults to None.

    Returns:
        tuple[Any, ...] | None: The result of the query, or None if there are none.
    """
    rows = query_all(connection, sql, params)
    return rows[0] if rows else None


def pretty_table(
    reporter: Reporter,
    title: str,
    headers: Sequence[str],
    rows: Iterable[Sequence[Any]],
    max_rows: int | None = None,
) -> None:
    """Write a pretty table to represent the data obtained.

    Args:
        reporter (Reporter): The Reporter to write with.
        title (str): The title of the subsection.
        headers (Sequence[str]): The headers of the table.
        rows (Iterable[Sequence[Any]]): The rows of the table.
        max_rows (int | None, optional): The maximum rows of the table.
            Defaults to None.
    """
    reporter.subsection(title)

    rows = list(rows)
    if max_rows is not None:
        rows = rows[:max_rows]

    if not rows:
        reporter.write("(no data)")
        return

    str_rows = [[str(v) for v in row] for row in rows]
    str_headers = [str(h) for h in headers]

    col_count = len(str_headers)
    widths = [len(h) for h in str_headers]

    for row in str_rows:
        for i in range(col_count):
            widths[i] = max(widths[i], len(row[i]))

    is_numeric_col = [True] * col_count
    for col in range(col_count):
        for row in str_rows:
            cell = row[col].strip()
            if not cell:
                continue
            try:
                float(cell)
            except ValueError:
                is_numeric_col[col] = False
                break

    def fmt_row(row_vals: Sequence[str]) -> str:
        parts = []
        for i, val in enumerate(row_vals):
            if is_numeric_col[i]:
                parts.append(val.rjust(widths[i]))
            else:
                parts.append(val.ljust(widths[i]))
        return " ".join(parts)

    # header
    reporter.write(fmt_row(str_headers))
    reporter.write(" ".join("-" * w for w in widths))

    # rows
    for row in str_rows:
        reporter.write(fmt_row(row))


def run_stats(
    connection: sqlite3.Connection,
    reporter: Reporter,
    *,
    top_n: int,
    min_messages_for_derived: int,
) -> None:
    """Run stats on the given database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
        top_n (int): The top n number of items to list.
        min_messages_for_derived (int): The minimum number of messages
            for derived statistics to be tracked.
    """
    # --- global overview ---
    reporter.section("Global Overview")

    row = query_one(
        connection,
        """--sql
        SELECT
            COUNT(*)                   AS total_messages,
            SUM(word_count)            AS total_words,
            SUM(char_count)            AS total_chars,
            SUM(attachment_count)      AS total_attachments,
            SUM(image_count)           AS total_images,
            SUM(video_count)           AS total_videos,
            SUM(sticker_count)         AS total_stickers,
            SUM(embed_count)           AS total_embeds,
            COUNT(DISTINCT author_id)  AS unique_authors,
            COUNT(DISTINCT channel_id) AS unique_channels
        FROM messages;
        """,
    )

    if row is None:
        reporter.write("No messages in database.")
        return

    (
        total_messages,
        total_words,
        total_chars,
        total_attachments,
        total_images,
        total_videos,
        total_stickers,
        total_embeds,
        unique_authors,
        unique_channels,
    ) = row

    time_row = query_one(
        connection,
        """--sql
        SELECT MIN(created_at), MAX(created_at)
        FROM messages;
        """,
    )
    oldest, newest = time_row if time_row else (None, None)

    reporter.write(f"Total messages:    {total_messages}")
    reporter.write(f"Total words:       {total_words}")
    reporter.write(f"Total characters:  {total_chars}")
    reporter.write(f"Total attachments: {total_attachments}")
    reporter.write(f"  - images:        {total_images}")
    reporter.write(f"  - videos:        {total_videos}")
    reporter.write(f"  - stickers:      {total_stickers}")
    reporter.write(f"Total embeds:      {total_embeds}")
    reporter.write(f"Unique authors:    {unique_authors}")
    reporter.write(f"Unique channels:   {unique_channels}")
    reporter.write(f"Oldest message:    {oldest}")
    reporter.write(f"Newest message:    {newest}")

    # --- top users & basic leaderboards ---
    reporter.section("User Leaderboards")

    # top message senders
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, COUNT(*) AS messages
        FROM messages
        GROUP BY author_id
        ORDER BY messages DESC;
        """,
    )
    pretty_table(reporter, "Top by Messages", ["author_id", "messages"], rows, top_n)

    # top word count
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, SUM(word_count) AS total_words
        FROM messages
        GROUP BY author_id
        ORDER BY total_words DESC;
        """,
    )
    pretty_table(reporter, "Top by Words", ["author_id", "total_words"], rows, top_n)

    # top char count
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, SUM(char_count) AS total_chars
        FROM messages
        GROUP BY author_id
        ORDER BY total_chars DESC;
        """,
    )
    pretty_table(
        reporter, "Top by Characters", ["author_id", "total_chars"], rows, top_n
    )

    # --- attachments / media stats ---
    reporter.section("Media & Attachment Leaderboards")

    # overall
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, SUM(attachment_count) AS attachments
        FROM messages
        GROUP BY author_id
        ORDER BY attachments DESC;
        """,
    )
    pretty_table(
        reporter, "Top by Attachments", ["author_id", "attachments"], rows, top_n
    )

    # images
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, SUM(image_count) AS images
        FROM messages
        GROUP BY author_id
        ORDER BY images DESC;
        """,
    )
    pretty_table(reporter, "Top by Images", ["author_id", "images"], rows, top_n)

    # videos
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, SUM(video_count) AS videos
        FROM messages
        GROUP BY author_id
        ORDER BY videos DESC;
        """,
    )
    pretty_table(reporter, "Top by Videos", ["author_id", "videos"], rows, top_n)

    # stickers
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, SUM(sticker_count) AS stickers
        FROM messages
        GROUP BY author_id
        ORDER BY stickers DESC;
        """,
    )
    pretty_table(reporter, "Top by Stickers", ["author_id", "stickers"], rows, top_n)

    # embeds
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, SUM(embed_count) AS embeds
        FROM messages
        GROUP BY author_id
        ORDER BY embeds DESC;
        """,
    )
    pretty_table(reporter, "Top by Embeds", ["author_id", "embeds"], rows, top_n)

    # --- message style stats ---
    reporter.section("Message Style Stats")

    # average words per message
    rows = query_all(
        connection,
        """--sql
        SELECT author_id,
            COUNT(*) AS messages,
            SUM(word_count) AS total_words,
            ROUND(1.0 * SUM(word_count) / COUNT(*), 2) AS avg_words_per_message
        FROM messages
        GROUP BY author_id
        HAVING messages >= ?
        ORDER BY avg_words_per_message DESC;
        """,
        (min_messages_for_derived,),
    )
    pretty_table(
        reporter,
        f"Yapaholics (min {min_messages_for_derived} msgs)",
        ["author_id", "messages", "total_words", "avg_words_per_message"],
        rows,
        top_n,
    )

    # media-first vs text-first (attachments %)
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, COUNT(*) AS messages,
            SUM(CASE WHEN attachment_count > 0 THEN 1 ELSE 0 END)
                AS msgs_with_attachments,
            ROUND(100.0 * SUM(
                CASE WHEN attachment_count > 0 THEN 1 ELSE 0 END
            ) / COUNT(*), 1) AS pct_with_attachments
        FROM messages
        GROUP BY author_id
        HAVING messages >= ?
        ORDER BY pct_with_attachments DESC;
        """,
        (min_messages_for_derived,),
    )
    pretty_table(
        reporter,
        f"Media-First Users (min {min_messages_for_derived} msgs)",
        ["author_id", "messages", "msgs_with_attachments", "pct_with_attachments"],
        rows,
        top_n,
    )

    # --- time-of-day stats ---
    reporter.section("Time-of-Day Stats")

    # night owls (midnight-4am EST; UTC-5 approximation)
    rows = query_all(
        connection,
        """--sql
        WITH per_user AS (
            SELECT author_id,
                COUNT(*) AS total_messages,
                SUM(
                    CASE
                    WHEN CAST(
                        strftime('%H', datetime(created_at, '-5 hours')) AS INTEGER)
                        BETWEEN 0 AND 3
                        THEN 1 ELSE 0
                    END
                ) AS night_messages
            FROM messages
            GROUP BY author_id
        )
        SELECT author_id,
            total_messages,
            night_messages,
            ROUND(100.0 * night_messages / total_messages, 1) AS night_pct
        FROM per_user
        WHERE total_messages >= ?
        ORDER BY night_pct DESC, night_messages DESC;
        """,
        (min_messages_for_derived,),
    )
    pretty_table(
        reporter,
        f"Night Owls (00:00-04:00 EST, min {min_messages_for_derived} msgs)",
        ["author_id", "total_messages", "night_messages", "night_pct"],
        rows,
        top_n,
    )

    # early birds (4am-8am EST; UTC-5 approximation)
    rows = query_all(
        connection,
        """--sql
        SELECT author_id,
            COUNT(*) AS morning_messages
        FROM messages
        WHERE CAST(strftime('%H', datetime(created_at, '-5 hours')) AS INTEGER)
            BETWEEN 4 AND 7
        GROUP BY author_id
        ORDER BY morning_messages DESC;
        """,
    )
    pretty_table(
        reporter,
        "Early Birds (04:00-08:00 EST)",
        ["author_id", "morning_messages"],
        rows,
        top_n,
    )

    # most active hours globally (eastern)
    rows = query_all(
        connection,
        """--sql
        SELECT strftime('%H', datetime(created_at, '-5 hours')) AS hour_est,
            COUNT(*) AS messages
        FROM messages
        GROUP BY hour_est
        ORDER BY hour_est;
        """,
    )
    pretty_table(
        reporter,
        "Messages by Hour of Day (EST, UTC-5 approx)",
        ["hour_est", "messages"],
        rows,
        None,
    )

    # messages by weekday
    rows = query_all(
        connection,
        """--sql
        SELECT strftime('%w', created_at) AS weekday,  -- 0=Sunday
            COUNT(*) AS messages
        FROM messages
        GROUP BY weekday
        ORDER BY messages DESC;
        """,
    )
    pretty_table(
        reporter,
        "Messages by Weekday (0=Sun, 6=Sat)",
        ["weekday", "messages"],
        rows,
        None,
    )

    # --- channel stats ---
    reporter.section("Channel Stats")

    # most active channels
    rows = query_all(
        connection,
        """--sql
        SELECT channel_id, COUNT(*) AS messages
        FROM messages
        GROUP BY channel_id
        ORDER BY messages DESC;
        """,
    )
    pretty_table(
        reporter, "Top Channels by Messages", ["channel_id", "messages"], rows, top_n
    )

    # channels with most media
    rows = query_all(
        connection,
        """--sql
        SELECT channel_id,
            SUM(image_count)    AS images,
            SUM(video_count)    AS videos,
            SUM(attachment_count) AS attachments
        FROM messages
        GROUP BY channel_id
        ORDER BY attachments DESC;
        """,
    )
    pretty_table(
        reporter,
        "Top Channels by Attachments",
        ["channel_id", "images", "videos", "attachments"],
        rows,
        top_n,
    )

    # wordiest channels
    rows = query_all(
        connection,
        """--sql
        SELECT channel_id,
            COUNT(*) AS messages,
            SUM(word_count) AS total_words,
            ROUND(1.0 * SUM(word_count) / COUNT(*), 2) AS avg_words_per_message
        FROM messages
        GROUP BY channel_id
        HAVING messages >= 200
        ORDER BY avg_words_per_message DESC;
        """,
    )
    pretty_table(
        reporter,
        "Wordiest Channels (min 200 msgs)",
        ["channel_id", "messages", "total_words", "avg_words_per_message"],
        rows,
        top_n,
    )

    # --- fun derived stats ---
    reporter.section("Fun Derived Stats")

    # expressive texters (high words, low media)
    rows = query_all(
        connection,
        """--sql
        WITH per_user AS (
            SELECT author_id,
                COUNT(*) AS messages,
                SUM(word_count) AS total_words,
                SUM(attachment_count) AS attachments
            FROM messages
            GROUP BY author_id
        )
        SELECT author_id,
            messages,
            total_words,
            attachments,
            ROUND(1.0 * total_words / messages, 2) AS avg_words_per_message,
            ROUND(1.0 * attachments / messages, 2) AS attachments_per_message
        FROM per_user
        WHERE messages >= ?
        ORDER BY avg_words_per_message DESC, attachments_per_message ASC;
        """,
        (min_messages_for_derived,),
    )
    pretty_table(
        reporter,
        f"Expressive Texters (min {min_messages_for_derived} msgs)",
        [
            "author_id",
            "messages",
            "total_words",
            "attachments",
            "avg_words_per_message",
            "attachments_per_message",
        ],
        rows,
        top_n,
    )

    # longest single messages (by word count)
    rows = query_all(
        connection,
        """--sql
        SELECT author_id, message_id, word_count, char_count, created_at
        FROM messages
        ORDER BY word_count DESC
        LIMIT ?;
        """,
        (top_n,),
    )
    pretty_table(
        reporter,
        "Longest Single Messages (by words)",
        ["author_id", "message_id", "word_count", "char_count", "created_at"],
        rows,
        None,
    )

    # spam gods (low avg words, high message count)
    rows = query_all(
        connection,
        """--sql
        WITH per_user AS (
            SELECT author_id,
                COUNT(*) AS messages,
                SUM(word_count) AS total_words
            FROM messages
            GROUP BY author_id
        )
        SELECT author_id,
            messages,
            total_words,
            ROUND(1.0 * total_words / messages, 2) AS avg_words_per_message
        FROM per_user
        WHERE messages >= ?
        ORDER BY avg_words_per_message ASC, messages DESC;
        """,
        (min_messages_for_derived,),
    )
    pretty_table(
        reporter,
        f"Spam Gods (min {min_messages_for_derived} msgs)",
        ["author_id", "messages", "total_words", "avg_words_per_message"],
        rows,
        top_n,
    )


def main() -> None:
    """Run stats on the DB and print them to a file."""
    parser = ArgumentParser(
        description="Analyze Cat Scan SQLite metrics and print a report."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(
            "data/cat_scan/cat_scan_2025.sqlite",
        ),
        help="Path to the SQLite database file "
        "(default: data/cat_scan/cat_scan_2025.sqlite)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("cat_scan_report.txt"),
        help="Path to the output text report file",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of rows to show for most leaderboards (default: 20)",
    )
    parser.add_argument(
        "--min-messages",
        type=int,
        default=50,
        help="Minimum messages to require for a a user to be "
        "included in derived stats (default: 50)",
    )

    args = parser.parse_args()

    if not args.db.is_file():
        raise SystemExit(f"Database file not found: {args.db}")

    connection = sqlite3.connect(args.db)
    try:
        reporter = Reporter(args.out)
        try:
            run_stats(
                connection,
                reporter,
                top_n=args.top,
                min_messages_for_derived=args.min_messages,
            )
            reporter.write()
            reporter.write(f"Report written to: {args.out.resolve()}")
        finally:
            reporter.close()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
