# pylint: disable=all

import inspect
import sys
from abc import abstractmethod
from typing import (
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    TextIO,
    Tuple,
    TypeAlias,
    Union,
    overload,
)

class SupportsStr(Protocol):
    def __str__(self) -> str: ...

class SupportsRepr(Protocol):
    def __repr__(self) -> str: ...

DEFAULT_FORMAT: Literal["[{ftime}] [{level}] {name} - {message} ({filename}:{lineno})"]
DEFAULT_TIMESTAMP_FORMAT: Literal["%Y-%m-%d %H:%M:%S"]
OpenTextWritingMode: TypeAlias = Literal[
    "r+",
    "+r",
    "rt+",
    "r+t",
    "+rt",
    "tr+",
    "t+r",
    "+tr",
    "w+",
    "+w",
    "wt+",
    "w+t",
    "+wt",
    "tw+",
    "t+w",
    "+tw",
    "a+",
    "+a",
    "at+",
    "a+t",
    "+at",
    "ta+",
    "t+a",
    "+ta",
    "x+",
    "+x",
    "xt+",
    "x+t",
    "+xt",
    "tx+",
    "t+x",
    "+tx",
    "w",
    "wt",
    "tw",
    "a",
    "at",
    "ta",
    "x",
    "xt",
    "tx",
]

@overload
def get_logger(id: int, name: str, /) -> Union[Logger, None]: ...
@overload
def get_logger(id: int, /) -> Union[Logger, None]: ...
@overload
def get_logger(name: str, /) -> Union[Logger, None]: ...

class _NoLogLevelSentinel:
    __slots__: Tuple[()]
    def __eq__(self, other: object) -> bool: ...
    def __bool__(self) -> Literal[False]: ...
    def __hash__(self) -> Literal[0]: ...
    def __repr__(self) -> Literal["NO_LEVEL_SET"]: ...

NO_LEVEL_SET: _NoLogLevelSentinel
DEBUG: Literal[1]
COMMAND_CALL: Literal[2]
CALL: Literal[2]
INFO: Literal[3]
SETUP: Literal[4]
WARNING: Literal[5]
WARN: Literal[5]
ERROR: Literal[6]
FATAL: Literal[7]

def get_level(
    level: Union[int, str], /
) -> Union[Literal[1, 2, 3, 4, 5, 6, 7], None]: ...
def get_level_name(level: Union[int, str], /) -> Union[
    Literal[
        "DEBUG",
        "COMMAND_CALL",
        "CALL",
        "INFO",
        "SETUP",
        "WARNING",
        "WARN",
        "ERROR",
        "FATAL",
    ],
    None,
]: ...

class LogMessage:
    def __init__(
        self,
        message: Union[SupportsStr, SupportsRepr],
        /,
        level: int | str,
        logger_name: str,
        stack_frame: inspect.FrameInfo,
    ) -> None: ...
    @property
    def message(self) -> str: ...
    @property
    def level(
        self,
    ) -> Literal[
        "DEBUG",
        "COMMAND_CALL",
        "CALL",
        "INFO",
        "SETUP",
        "WARNING",
        "WARN",
        "ERROR",
        "FATAL",
    ]: ...
    @property
    def levelno(self) -> Literal[1, 2, 3, 4, 5, 6, 7]: ...
    @property
    def logger_name(self) -> str: ...
    @property
    def filepath(self) -> str: ...
    @property
    def filename(self) -> str: ...
    @property
    def module(self) -> str: ...
    @property
    def lineno(self) -> int: ...
    @property
    def time(self) -> float: ...

class Formatter:
    def __init__(
        self,
        template: str = DEFAULT_FORMAT,
        timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
        end: str = "\n",
    ) -> None: ...
    def format(self, message: LogMessage, /) -> str: ...
    @property
    def template(self) -> str: ...
    @template.setter
    def template(self, new: str) -> None: ...
    @property
    def timestamp_format(self) -> str: ...
    @timestamp_format.setter
    def timestamp_format(self, new: str) -> None: ...
    @property
    def end(self) -> str: ...
    @end.setter
    def end(self, new: str) -> None: ...

default_formatter: Formatter

class LoggerOutput:
    def __init__(self) -> None: ...
    @abstractmethod
    def send(self, message: str, /) -> None: ...
    @property
    def id(self) -> int: ...
    @property
    def formatter(self) -> Union[Formatter, None]: ...
    @formatter.setter
    def formatter(self, new: Formatter) -> None: ...
    def remove_formatter(self) -> None: ...

class StreamOutput(LoggerOutput):
    def __init__(self, stream: TextIO = sys.stderr, /) -> None: ...
    def send(self, message: str, /) -> None: ...
    @property
    def stream(self) -> TextIO: ...

class FileOutput(LoggerOutput):
    def __init__(
        self,
        filepath: str,
        mode: OpenTextWritingMode = "a",
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
    ) -> None: ...
    def send(self, message: str, /) -> None: ...
    @property
    def filepath(self) -> str: ...
    @property
    def open_text_mode(self) -> str: ...
    @property
    def encoding(self) -> Union[str, None]: ...
    @property
    def errors(self) -> Union[str, None]: ...

class Logger:
    def __init__(self, name: str, level: Union[int, str]) -> None: ...
    @overload
    def log(
        self, message: Union[SupportsStr, SupportsRepr], level: Union[int, str], /
    ) -> None: ...
    @overload
    def log(
        self,
        message: Union[SupportsStr, SupportsRepr],
        level: _NoLogLevelSentinel = NO_LEVEL_SET,
        /,
    ) -> None: ...
    def debug(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def command_call(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def CALL(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def info(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def setup(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def warning(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def warn(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def error(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def fatal(self, message: Union[SupportsStr, SupportsRepr], /) -> None: ...
    def add_output(self, output: LoggerOutput, /) -> None: ...
    @overload
    def remove_output(self, output: LoggerOutput, /) -> None: ...
    @overload
    def remove_output(self, id: int, /) -> None: ...
    def clear_outputs(self) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def formatter(self) -> Formatter: ...
    @formatter.setter
    def formatter(self, new: Formatter) -> None: ...
    @property
    def outputs(self) -> List[LoggerOutput]: ...
    @property
    def id(self) -> int: ...
    @property
    def level(
        self,
    ) -> Literal[
        "DEBUG",
        "COMMAND_CALL",
        "CALL",
        "INFO",
        "SETUP",
        "WARNING",
        "WARN",
        "ERROR",
        "FATAL",
    ]: ...
    @level.setter
    def level(self, new: Union[int, str]) -> None: ...
    @property
    def levelno(self) -> Literal[1, 2, 3, 4, 5, 6, 7]: ...
    @property
    def enabled(self) -> bool: ...
    @enabled.setter
    def enabled(self, new: bool) -> None: ...

root: Logger

def config_root(
    *,
    level: Optional[Union[int, str]] = None,
    formatter: Optional[Formatter] = None,
    outputs: Optional[Sequence[LoggerOutput]] = None,
    enabled: Optional[bool] = None,
    filepath: Optional[str] = None,
) -> None: ...
def reset_root() -> None: ...
@overload
def log(
    message: Union[SupportsStr, SupportsRepr], level: Union[int, str], /
) -> None: ...
@overload
def log(
    message: Union[SupportsStr, SupportsRepr],
    level: _NoLogLevelSentinel = NO_LEVEL_SET,
    /,
) -> None: ...
def debug(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def command_call(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def call(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def info(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def setup(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def warning(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def warn(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def error(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
def fatal(message: Union[SupportsStr, SupportsRepr], /) -> None: ...
