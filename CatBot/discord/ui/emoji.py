"""Strings that are converted into Discord emojis when written by the bot."""

from enum import StrEnum

__author__ = "Gavin Borne"
__license__ = "MIT"


class Status(StrEnum):
    """A class of status-related emojis."""

    SUCCESS = ":white_check_mark:"
    """A check mark indicating a successful operation."""
    FAILURE = ":x:"
    """An X representing the failure of an operation."""
    CANCELLED = ":octagonal_sign:"
    """An octagonal sign resembling a stop sign for cancelled events."""
    WARNING = ":warning:"
    """A warning symbol for possible incidents."""
    ERROR = ":interrobang:"
    """A red exclamation mark and question mark for when something went wrong."""


class Visual(StrEnum):
    """A class for visual emojis that are purely for aesthetics."""

    ART_PALETTE = ":art:"
    STOPWATCH = ":stopwatch:"
    CHART = ":bar_chart:"
    COIN = ":coin:"
    PHOTO = ":frame_photo:"
    CAT = ":cat:"
    PEOPLE_SYMBOL = ":family_adult_adult_child_child:"
    QUESTION_MARK = ":grey_question:"
    HAMMER = ":hammer:"
    ALARM_CLOCK = ":alarm_clock:"
    ALERT = ":exclamation:"
    RANDOM = ":twisted_rightwards_arrows:"
    MATH = ":hash:"
    PAWS = ":feet:"
