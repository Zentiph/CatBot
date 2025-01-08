"""
pawprints
---------
pawprints is a custom logging library developed for CatBot to allow for more detailed logging
as well as preventing discord.py logs from appearing when using logging in DEBUG mode.
"""

__all__ = [
    "CMD_CALL",
    "COMMAND_CALL",
    "DEBUG",
    "DEFAULT_FORMAT",
    "DEFAULT_TIMESTAMP_FORMAT",
    "ERROR",
    "FATAL",
    "INFO",
    "NO_LEVEL_SET",
    "SETUP",
    "WARN",
    "WARNING",
    "FileOutput",
    "Formatter",
    "Logger",
    "LogMessage",
    "StreamOutput",
    "cmd_call",
    "command_call",
    "config_root",
    "debug",
    "default_formatter",
    "error",
    "fatal",
    "get_level",
    "get_level_name",
    "get_logger",
    "info",
    "log",
    "reset_root",
    "root",
    "setup",
    "warn",
    "warning",
]

from .pawprints import (
    CMD_CALL,
    COMMAND_CALL,
    DEBUG,
    DEFAULT_FORMAT,
    DEFAULT_TIMESTAMP_FORMAT,
    ERROR,
    FATAL,
    INFO,
    NO_LEVEL_SET,
    SETUP,
    WARN,
    WARNING,
    FileOutput,
    Formatter,
    Logger,
    LogMessage,
    StreamOutput,
    cmd_call,
    command_call,
    config_root,
    debug,
    default_formatter,
    error,
    fatal,
    get_level,
    get_level_name,
    get_logger,
    info,
    log,
    reset_root,
    root,
    setup,
    warn,
    warning,
)
