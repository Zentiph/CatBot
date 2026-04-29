"""Analyze the wrapped database to get stats."""

from argparse import ArgumentParser
from collections.abc import Iterable, Sequence
import contextlib
from pathlib import Path
import sqlite3
from typing import Any, Protocol

__author__ = "Gavin Borne"
__license__ = "MIT"


class _SupportsStr(Protocol):
    def __str__(self) -> str: ...


class Reporter:
    """Writes outputs to both stdout and a log file."""

    def __init__(self, write_to: Path) -> None:
        """Writes outputs to both stdout and a log file.

        Args:
            write_to (Path): Where to write the report to.
        """
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


def fmt_row(
    row_vals: Sequence[str], widths: Sequence[int], is_numeric_col: Sequence[bool]
) -> str:
    """Format a row with its values, widths, and numeric states.

    Numeric columns are right-justified while others are left-justified.

    Args:
        row_vals (Sequence[str]): The values in the row.
        widths (Sequence[int]): The widths to fit each value in.
        is_numeric_col (Sequence[bool]): Whether each column is numeric.


    Returns:
        str: The formatted row as a string.
    """
    parts = []
    for i, val in enumerate(row_vals):
        if is_numeric_col[i]:
            parts.append(val.rjust(widths[i]))
        else:
            parts.append(val.ljust(widths[i]))
    return " ".join(parts)


def pretty_table(
    reporter: Reporter,
    title: str,
    headers: Sequence[str],
    rows: Iterable[Sequence[_SupportsStr]],
    max_rows: int | None = None,
) -> None:
    """Write a pretty table to represent the data obtained.

    Args:
        reporter (Reporter): The Reporter to write with.
        title (str): The title of the subsection.
        headers (Sequence[str]): The headers of the table.
        rows (Iterable[Sequence[_SupportsStr]]): The rows of the table.
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

    # header
    reporter.write(fmt_row(str_headers, widths, is_numeric_col))
    reporter.write(" ".join("-" * w for w in widths))

    # rows
    for row in str_rows:
        reporter.write(fmt_row(row, widths, is_numeric_col))


def run_global_overview_stats(
    connection: sqlite3.Connection, reporter: Reporter
) -> None:
    """Run global overview stats stats on the messages database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
    """
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


def run_top_users_and_basic_leaderboard_stats(
    connection: sqlite3.Connection, reporter: Reporter, *, top_n: int
) -> None:
    """Run top user and basic leaderboard stats on the messages database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
        top_n (int): The top n number of items to list per leaderboard.
    """
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


def run_attachments_and_media_stats(
    connection: sqlite3.Connection, reporter: Reporter, *, top_n: int
) -> None:
    """Run attachments and media stats on the messages database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
        top_n (int): The top n number of items to list per leaderboard.
    """
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


def run_message_style_stats(
    connection: sqlite3.Connection,
    reporter: Reporter,
    *,
    top_n: int,
    min_messages_for_derived: int,
) -> None:
    """Run message style stats on the messages database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
        top_n (int): The top n number of items to list per leaderboard.
        min_messages_for_derived (int): The minimum number of messages
            for derived statistics to be tracked.
    """
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


def run_time_of_day_stats(
    connection: sqlite3.Connection,
    reporter: Reporter,
    *,
    top_n: int,
    min_messages_for_derived: int,
) -> None:
    """Run time of day stats on the messages database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
        top_n (int): The top n number of items to list per leaderboard.
        min_messages_for_derived (int): The minimum number of messages
            for derived statistics to be tracked.
    """
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


def run_channel_stats(
    connection: sqlite3.Connection,
    reporter: Reporter,
    *,
    top_n: int,
) -> None:
    """Run channel stats on the messages database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
        top_n (int): The top n number of items to list per leaderboard.
    """
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


def run_stats(
    connection: sqlite3.Connection,
    reporter: Reporter,
    *,
    top_n: int,
    min_messages_for_derived: int,
) -> None:
    """Run stats on the messages database.

    Args:
        connection (sqlite3.Connection): The DB to run stats on.
        reporter (Reporter): The Reporter to report with.
        top_n (int): The top n number of items to list per leaderboard.
        min_messages_for_derived (int): The minimum number of messages
            for derived statistics to be tracked.
    """
    reporter.section("Global Overview")
    run_global_overview_stats(connection, reporter)

    reporter.section("User Leaderboards")
    run_top_users_and_basic_leaderboard_stats(connection, reporter, top_n=top_n)

    reporter.section("Media & Attachment Leaderboards")
    run_attachments_and_media_stats(connection, reporter, top_n=top_n)

    reporter.section("Message Style Stats")
    run_message_style_stats(
        connection,
        reporter,
        top_n=top_n,
        min_messages_for_derived=min_messages_for_derived,
    )

    reporter.section("Time-of-Day Stats")
    run_time_of_day_stats(
        connection,
        reporter,
        top_n=top_n,
        min_messages_for_derived=min_messages_for_derived,
    )

    reporter.section("Channel Stats")
    run_channel_stats(
        connection,
        reporter,
        top_n=top_n,
    )


def main() -> None:
    """Run stats on the DB and print them to a file."""
    parser = ArgumentParser(
        description="Analyze wrapped SQLite metrics and print a report."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(
            "data/wrapped/wrapped_2025.sqlite",
        ),
        help="Path to the SQLite database file "
        "(default: data/wrapped/wrapped_2025.sqlite)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("wrapped_report.txt"),
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
