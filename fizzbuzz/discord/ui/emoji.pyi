from enum import StrEnum
from typing import Final

__author__: Final[str]
__license__: Final[str]

class Status(StrEnum):
    SUCCESS = "✅"
    FAILURE = "❌"
    CANCELLED = "🛑"
    WARNING = "⚠️"
    ERROR = "⁉️"

class Visual(StrEnum):
    ART_PALETTE = "🎨"
    STOPWATCH = "⏱️"
    CHART = "📊"
    COIN = "🪙"
    PHOTO = "🖼️"
    CAT = "🐱"
    COMPUTER = "🖥️"
    PEOPLE_SYMBOL = "🧑‍🧑‍🧒‍🧒"
    QUESTION_MARK = "❔"
    HAMMER = "🔨"
    ALARM_CLOCK = "⏰"
    ALERT = "❗"
    RANDOM = "🎲"
    PAWS = "🐾"
    NEXT = "▶️"
    PREVIOUS = "◀️"
    HANDSHAKE = "🤝"
    SODA = "🥤"
