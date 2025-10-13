from enum import StrEnum

class Status(StrEnum):
    SUCCESS = ":white_check_mark:"
    FAILURE = ":x:"
    CANCELLED = ":octagonal_sign:"
    WARNING = ":warning:"
    ERROR = ":interrobang:"

class Visual(StrEnum):
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
