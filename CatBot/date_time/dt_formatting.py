"""
dt_formatting.py
Formatting functionality for working with datetime.
"""

import datetime

NUMBER_TO_DAY = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
NUMBER_TO_MONTH = [
    "",  # Blank spot for month == 0
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def number_to_time(number: int, /) -> str:
    """
    Convert `number` to a time number.
    (i.e. 8 -> "08")

    :param number: Number to convert
    :type number: int
    :return: Time representation of `number`
    :rtype: str
    """

    string = str(number)
    if number <= 10:
        return "0" + string
    return string


def format_date(date: datetime.date) -> str:
    """
    Format `date` into a str.

    :param date: datetime.date object
    :type date: datetime.date
    :return: Formatted date
    :rtype: str
    """

    weekday = NUMBER_TO_DAY[date.weekday()]
    day = date.day
    month = NUMBER_TO_MONTH[date.month]
    year = date.year

    return f"{weekday}, {month} {day}, {year}"


def format_time(
    time: datetime.time,
    military: bool = False,
    seconds: bool = False,
    microseconds: bool = False,
) -> str:
    """
    Format `time` into a str.

    :param time: datetime.time object
    :type time: datetime.time
    :param military: Whether to use military (24-hour) time, defaults to False
    :type military: bool, optional
    :param seconds: Whether to include seconds, defaults to False
    :type seconds: bool, optional
    :param microseconds: Whether to include microseconds
    (automatically includes seconds as well), defaults to False
    :type microseconds: bool, optional
    :return: Formatted time
    :rtype: str
    """

    init_hour = time.hour
    meridiem = ""
    if not military:
        if init_hour >= 12:
            meridiem = " PM"
        else:
            meridiem = " AM"

        if init_hour > 12:
            init_hour -= 12
        elif init_hour == 0:
            init_hour = 12

    hour = number_to_time(int(init_hour))
    minute = number_to_time(time.minute)
    second = ":" + number_to_time(time.second) if seconds or microseconds else ""
    micro = "." + str(time.microsecond) if microseconds else ""

    return f"{hour}:{minute}{second}{micro}{meridiem}"


def format_datetime(
    dt: datetime.datetime,
    military: bool = False,
    seconds: bool = False,
    microseconds: bool = False,
) -> str:
    """
    Format `dt` into a str.

    :param dt: datetime.datetime object
    :type dt: datetime.time
    :param military: Whether to use military (24-hour) time, defaults to False
    :type military: bool, optional
    :param seconds: Whether to include seconds, defaults to False
    :type seconds: bool, optional
    :param microseconds: Whether to include microseconds, defaults to False
    :type microseconds: bool, optional
    :return: Formatted datetime
    :rtype: str
    """

    return (
        format_date(dt.date())
        + "\n"
        + format_time(dt.time(), military, seconds, microseconds)
    )
