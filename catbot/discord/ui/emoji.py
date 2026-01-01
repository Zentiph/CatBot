"""Strings that are converted into Discord emojis when written by the bot."""

from enum import StrEnum

__author__ = "Gavin Borne"
__license__ = "MIT"


class Status(StrEnum):
    """A class of status-related emojis."""

    SUCCESS = "✅"
    """A check mark indicating a successful operation."""
    FAILURE = "❌"
    """An X representing the failure of an operation."""
    CANCELLED = "🛑"
    """An octagonal sign resembling a stop sign for cancelled events."""
    WARNING = "⚠️"
    """A warning symbol for possible incidents."""
    ERROR = "⁉️"
    """A red exclamation mark and question mark for when something went wrong."""


class Visual(StrEnum):
    """A class for visual emojis that are purely for aesthetics."""

    ART_PALETTE = "🎨"
    STOPWATCH = "⏱️"
    CHART = "📊"
    COIN = "🪙"
    PHOTO = "🖼️"
    CAT = "🐱"
    PEOPLE_SYMBOL = "🧑‍🧑‍🧒‍🧒"
    QUESTION_MARK = "❔"
    HAMMER = "🔨"
    ALARM_CLOCK = "⏰"
    ALERT = "❗"
    RANDOM = "🎲"
    PAWS = "🐾"
    NEXT = "▶️"
    PREVIOUS = "◀️"
