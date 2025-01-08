"""
pawprints.py
Main file for the pawprints library.
"""

from abc import abstractmethod
from inspect import FrameInfo, stack
from io import TextIOBase, SEEK_END
from os.path import basename
from sys import stderr
from time import gmtime, strftime, time
from typing import Dict, List


DEFAULT_FORMAT = "[{ftime}] [{level}] {name} - {message} ({filename}:{lineno})"
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
_OPEN_TEXT_WRITING_MODES = (
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
)

_loggers: Dict[int, "Logger"] = {}
_loggers_by_name: Dict[str, "Logger"] = {}
_outputs: Dict[int, "_LoggerOutput"] = {}
# We define these as lists so we can access them anywhere without use of 'global'
_most_recent_logger_id: List[int] = [-1]
_most_recent_output_id: List[int] = [-1]


def _generate_new_logger_id():
    """
    Generate a new logger id based on existing loggers.
    """

    if _most_recent_logger_id[0] == -1:  # Not yet initialized
        _most_recent_logger_id[0] = 0
        return 0

    _most_recent_logger_id[0] += 1
    return _most_recent_logger_id[0]


def _generate_new_output_id():
    """
    Generate a new output id based on existing outputs.
    """

    if _most_recent_output_id[0] == -1:  # Not yet initialized
        _most_recent_output_id[0] = 0
        return 0

    _most_recent_output_id[0] += 1
    return _most_recent_output_id[0]


def _try_to_string(obj, /):
    """
    Attempt to convert the object to a str.
    Return the stringified object if successful, otherwise return False.

    :param obj: Object to attempt to convert
    :type obj: object
    :return: The stringified object or None if unsuccessful
    :rtype: str | None
    """

    if hasattr(obj, "__str__"):
        return str(obj)
    if hasattr(obj, "__repr__"):
        return repr(obj)
    return None


def get_logger(*args):
    """
    Get a Logger from its name or its id.

    :param name: The Logger's name
    :type name: str
    :param id: The Logger's id
    :type id: int
    :return: The Logger matching the given input(s) if found, otherwise None
    :rtype: pawprints.Logger | None
    """

    if len(args) not in (1, 2):
        raise TypeError(
            f"get_logger takes 1 or 2 positional arguments but {len(args)} were given"
        )

    if len(args) == 2:
        id, name = args[0], args[1]  # pylint: disable=redefined-builtin

        if not isinstance(id, int):
            raise TypeError("id must be an int")
        if not isinstance(name, str):
            raise TypeError("name must be a str")

        logger_from_id = _loggers.get(id, None)
        if logger_from_id is not None and logger_from_id.name == name:
            return logger_from_id

        return None  # No Logger with the id and name given exists

    # elif len(args) == 1
    if isinstance(args[0], int):  # Arg is an id
        return _loggers.get(args[0], None)
    if isinstance(args[0], str):  # Arg is a name
        return _loggers_by_name.get(args[0], None)

    raise TypeError("when given 1 positional argument, get_logger takes an int or str")


class _NoLogLevelSentinel:
    """
    Sentinel for the NO_LEVEL_SET const.
    """

    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, _NoLogLevelSentinel)

    def __bool__(self):
        return False

    def __hash__(self):
        return 0

    def __repr__(self):
        return "NO_LEVEL_SET"


NO_LEVEL_SET = _NoLogLevelSentinel()
"""
NO_LEVEL_SET represents the absence of a logging level.
It is often used as an absorbent value where it will be replaced with another preset level.
"""
DEBUG = 1
"""
Level for testing.
"""
COMMAND_CALL = 2
"""
Level for tracing command calls.
"""
CMD_CALL = COMMAND_CALL
INFO = 3
"""
Level for tracking important information.
"""
SETUP = 4
"""
Level for tracing bot setup processes.
"""
WARNING = 5
"""
Level for warnings.
"""
WARN = WARNING
ERROR = 6
"""
Level for non-fatal errors.
"""
FATAL = 7
"""
Level for fatal errors.
"""

_level_name_to_number = {
    "DEBUG": 1,
    "COMMAND_CALL": 2,
    "CMD_CALL": 2,
    "INFO": 3,
    "SETUP": 4,
    "WARNING": 5,
    "WARN": 5,
    "ERROR": 6,
    "FATAL": 7,
}
_level_number_to_name = {
    1: "DEBUG",
    2: "COMMAND_CALL",
    3: "INFO",
    4: "SETUP",
    5: "WARNING",
    6: "ERROR",
    7: "FATAL",
}


def get_level(level, /):
    """
    Get the numeric logging level from the given level.
    The given value can be an int or a str.

    :param level: Logging level
    :type level: int | str
    :return: The logging level as an int, if found
    :rtype: int | None
    """

    if not isinstance(level, (int, str)):
        raise TypeError("level must be an int or str")

    if isinstance(level, str):
        return _level_name_to_number.get(level.upper(), None)

    if 1 <= level <= 7:
        return level
    return None


def get_level_name(level, /):
    """
    Get the named logging level from the given level.
    The given value can be an int or a str.

    :param level: Logging level
    :type level: int | str
    :return: The logging level as a str, if found
    :rtype: str
    """

    if not isinstance(level, (int, str)):
        raise TypeError("level must be an int or str")

    if isinstance(level, int):
        return _level_number_to_name.get(level, None)

    if level in (
        "DEBUG",
        "COMMAND_CALL",
        "CMD_CALL",
        "INFO",
        "SETUP",
        "WARNING",
        "WARN",
        "ERROR",
        "FATAL",
    ):
        return level
    return None


class LogMessage:  # pylint: disable=too-many-instance-attributes
    """
    Log message class.
    Essentially a string with extra stored information to improve time accuracy.
    """

    def __init__(
        self,
        message,
        /,
        level,
        logger_name,
        stack_frame,
    ):
        """
        Log message class.
        Essentially a string with extra stored information to improve time accuracy.

        :param message: Log message
        :type message: SupportsStr | SupportsRepr
        :param level: The log level used
        :type level: int | str
        :param logger_name: Name of the logger
        :type logger_name: str
        :param stack_frame: The stack frame where the log call was made
        :type stack_frame: inspect.FrameInfo
        """

        current_time = time()

        message = _try_to_string(message)
        if message is None:
            raise TypeError("message must be a str or support __str__ or __repr__")
        level = get_level(level)
        if level is None:
            raise ValueError("level must be a valid logging level (1-7)")
        if not isinstance(logger_name, str):
            raise TypeError("logger_name must be a str")
        if not isinstance(stack_frame, FrameInfo):
            raise TypeError("stack_frame must be an inspect.FrameInfo")

        self.__message = message
        self.__levelno = level
        self.__level = get_level_name(self.__levelno)
        self.__logger_name = logger_name
        self.__filepath = stack_frame.filename
        self.__filename = self.__filepath.split("\\")[-1]
        self.__lineno = stack_frame.lineno
        self.__module = basename(self.__filepath).removesuffix(".py")
        self.__time = current_time

    @property
    def message(self):
        """
        The original message of this LogMessage.
        """

        return self.__message

    @property
    def level(self):
        """
        The name of this LogMessage's logging level.
        """

        return self.__level

    @property
    def levelno(self):
        """
        The numeric value of this LogMessage's logging level.
        """

        return self.__levelno

    @property
    def logger_name(self):
        """
        The name of the Logger used to create this LogMessage.
        """

        return self.__logger_name

    @property
    def filepath(self):
        """
        The path to the file this LogMessage was created in.
        """

        return self.__filepath

    @property
    def filename(self):
        """
        The name of the file this LogMessage was created in.
        """

        return self.__filename

    @property
    def module(self):
        """
        The module name of the file this LogMessage was created in.
        """

        return self.__module

    @property
    def lineno(self):
        """
        The line number in the file this LogMessage was created in.
        """

        return self.__lineno

    @property
    def time(self):
        """
        The time.time() value generated when this LogMessage was created.
        """

        return self.__time


class Formatter:
    """
    Formatter for log messages.
    """

    def __init__(self, template, timestamp_format=DEFAULT_TIMESTAMP_FORMAT, end="\n"):
        """
        Formatter for log messages.

        :param template: Format to use when formatting log messages.
        Below is a list of important formatting variables.
        :type template: str
        :param timestamp_format: Format to use for timestamps
        :type timestamp_format: str
        :param end: String to terminate each message with, defaults to "\\n"
        :type end: str, optional

        Formatting variables:
        - {message} - The message to be logged
        - {level} - The name of the logging level used
        - {levelno} - The numeric value of the logging level used
        - {name} - The name of the Logger
        - {filepath} - The path of the file in which the log originated
        - {filename} - The name of the file in which the log originated
        - {module} - The name of the module in which the log originated (the name portion of {file})
        - {lineno} - The line number in the file in which the log originated
        - {time} - Numeric value of when the log was created (time.time() value)
        - {ftime} - Formatted text representation of the time the log was created
        """

        if not isinstance(template, str):
            raise TypeError("template must be a str")
        if not isinstance(timestamp_format, str):
            raise TypeError("timestamp_format must be a str")
        if not isinstance(end, str):
            raise TypeError("end must be a str")

        self.__template = template
        self.__timestamp_format = timestamp_format
        self.__end = end

    def format(self, message, /):
        """
        Format a log message using this Formatter's formatting template.

        :param message: Message to format
        :type message: LogMessage
        :return: The formatted message
        :rtype: str
        """

        if not isinstance(message, LogMessage):
            raise TypeError("message must be a pawprints.LogMessage")

        return (
            self.__template.format(
                message=message.message,
                level=message.level,
                levelno=message.levelno,
                name=message.logger_name,
                filepath=message.filepath,
                filename=message.filename,
                module=message.module,
                lineno=message.lineno,
                time=message.time,
                ftime=strftime(self.__timestamp_format, gmtime(message.time)),
            )
            + self.__end
        )

    @property
    def template(self):
        """
        The template being used by this Formatter to format logs.
        """

        return self.__template

    @template.setter
    def template(self, new):
        if not isinstance(new, str):
            raise TypeError("template must be a str")

        self.__template = new

    @property
    def timestamp_format(self):
        """
        The date format being used by this Formatter.
        """

        return self.__timestamp_format

    @timestamp_format.setter
    def timestamp_format(self, new):
        if not isinstance(new, str):
            raise TypeError("timestamp_format must be a str")

        self.__timestamp_format = new

    @property
    def end(self):
        """
        The terminating string appended to each message once formatted.
        """

        return self.__end

    @end.setter
    def end(self, new):
        if not isinstance(new, str):
            raise TypeError("end must be a str")

        self.__end = new


default_formatter = Formatter(DEFAULT_FORMAT)


class _LoggerOutput:  # pylint: disable=too-few-public-methods
    """
    Base class for logger output streams.
    """

    def __init__(self):
        """
        Base class for logger output streams.
        """

        self.__id = _generate_new_output_id()
        _outputs[self.__id] = self

    # this method should be overridden by subclasses
    @abstractmethod
    def send(self, message, /):
        """
        Send a log message through an output channel.

        :param message: Message to send
        :type message: SupportsStr | SupportsRepr
        """

    @property
    def id(self):
        """
        The id of the output.
        An output's id shows its place in the order of creation.
        Output ids start at 0 and grow by 1 for each new output.
        """

        return self.__id


class StreamOutput(_LoggerOutput):
    """
    Stream output handler for loggers.
    """

    def __init__(self, stream=stderr, /):
        """
        Stream output handler for loggers.

        :param stream: Stream to send the logger output to, defaults to sys.stderr
        :type stream: TextIO, optional
        """

        if not isinstance(stream, TextIOBase):
            raise TypeError("stream must be a TextIO")
        if not stream.writable():
            raise ValueError("stream is not writeable")

        super().__init__()
        self.__stream = stream

    def send(self, message, /):
        """
        Write a log message to the output stream.

        :param message: Message to send
        :type message: SupportsStr | SupportsRepr
        """

        stream = self.__stream
        stream.write(message)
        stream.flush()

    @property
    def stream(self):
        """
        The stream being used by this StreamOutput.
        """

        return self.__stream


class FileOutput(_LoggerOutput):
    """
    File output handler for loggers.
    """

    def __init__(self, filepath, mode="a", encoding=None, errors=None):
        """
        File output handler for loggers.

        :param filepath: Path to the file to write to
        :type filepath: str
        :param mode: Text writing mode, defaults to "a"
        :type mode: pawprints.TextWritingMode, optional
        :param encoding: Encoding to use, defaults to None
        :type encoding: str | None, optional
        :param errors: Specification regarding encoding error handling, defaults to None
        :type errors: str, optional
        """

        if not isinstance(filepath, str):
            raise TypeError("filepath must be a str")
        if not isinstance(mode, str):
            raise TypeError("mode must be a str")
        if mode not in _OPEN_TEXT_WRITING_MODES:
            raise ValueError("mode must be a text writing mode")
        if encoding is not None and not isinstance(encoding, str):
            raise TypeError("encoding must be a str or None")
        if errors is not None and not isinstance(errors, str):
            raise TypeError("errors must be a str or None")

        super().__init__()
        self.__filepath = filepath
        self.__mode = mode
        self.__encoding = encoding
        self.__errors = errors

    def send(self, message, /):
        """
        Write a log message to the output file.

        :param message: Message to send
        :type message: SupportsStr | SupportsRepr
        """

        with open(
            self.__filepath, self.__mode, encoding=self.__encoding, errors=self.__errors
        ) as file:
            if not file.writable():
                raise ValueError(f"file '{self.__filepath}' is not writable")

            file.seek(0, SEEK_END)
            file.write(message)
            file.flush()

    @property
    def filepath(self):
        """
        The path to this FileOutput's target file.
        """

        return self.__filepath

    @property
    def open_text_mode(self):
        """
        The file writing mode being used by this FileOutput.
        """

        return self.__mode

    @property
    def encoding(self):
        """
        The encoding used by this FileOutput.
        """

        return self.__encoding

    @property
    def errors(self):
        """
        The encoding error specification being used by this FileOutput.
        """

        return self.__errors


class Logger:  # pylint: disable=too-many-instance-attributes
    """
    A basic logger that can be used for one logging stream.
    """

    def __init__(self, name, level):
        """
        A basic logger that can be used for one logging stream.

        :param name: Name of the logger
        :type name: str
        :param level: Lowest logging level to track
        :type level: int | str, optional
        """

        if not isinstance(name, str):
            raise TypeError("name must be a str")
        level = get_level(level)
        if level is None:
            raise ValueError("level must be a valid logging level (1-7)")

        if name in _loggers_by_name:
            raise ValueError(
                f"a logger has already been initialized with name '{name}'"
            )

        self.__id = _generate_new_logger_id()
        _loggers[self.__id] = self
        self.__name = name
        _loggers_by_name[self.__name] = self

        self.__level = level
        self.__enabled = True
        self.__formatter = default_formatter
        self.__outputs = []

    def __log(self, message, level, /):
        """
        Log the given message with the given level.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        :param level: Logging level
        :type level: int | str
        """

        message = _try_to_string(message)
        if message is None:
            raise TypeError("message must be a str or support __str__ or __repr__")
        level = get_level(level)
        if level is None:
            raise ValueError("level must be a valid logging level (1-7)")

        if not self.__enabled:
            return
        if self.__level > level:
            return

        # Right here is level 1,
        # above that is where __log was called, which is level 2,
        # and above that is where a log function was called, which is level 3 and what we want.
        stack_level = 3

        log_message = LogMessage(message, level, self.__name, stack()[stack_level])
        out_message = self.__formatter.format(log_message)

        for output_handler in self.__outputs:
            output_handler.send(out_message)

    def log(self, message, level=NO_LEVEL_SET, /):
        """
        Create a log with the given message and level.
        If level is left as NO_LEVEL_SET, it will default to this Logger's set level.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        :param level: Logging level to use, defaults to NO_LEVEL_SET
        :type level: int | str | pawprints._NoLogLevelSentinel, optional
        """

        if level == NO_LEVEL_SET:
            level = self.__level

        self.__log(message, level)

    def debug(self, message, /):
        """
        Create a DEBUG level log with the given message.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        """

        self.__log(message, DEBUG)

    def command_call(self, message, /):
        """
        Create a CMD_CALL level log with the given message.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        """

        self.__log(message, CMD_CALL)

    cmd_call = command_call

    def info(self, message, /):
        """
        Create an INFO level log with the given message.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        """

        self.__log(message, INFO)

    def setup(self, message, /):
        """
        Create a SETUP level log with the given message.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        """

        self.__log(message, SETUP)

    def warning(self, message, /):
        """
        Create a WARNING level log with the given message.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        """

        self.__log(message, WARNING)

    warn = warning

    def error(self, message, /):
        """
        Create an ERROR level log with the given message.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        """

        self.__log(message, ERROR)

    def fatal(self, message, /):
        """
        Create a FATAL level log with the given message.

        :param message: Message to log
        :type message: SupportsStr | SupportsRepr
        """

        self.__log(message, FATAL)

    def add_output(self, output, /):
        """
        Add a logger output to this Logger.

        :param output: logger output to add; can be a _LoggerOutput instance or an output id
        :type output: _LoggerOutput | int
        """

        if isinstance(output, _LoggerOutput):
            self.__outputs.append(output)
            return

        if isinstance(output, int):
            if output_object := _outputs.get(output, None):
                self.__outputs.append(output_object)
                return
            raise ValueError(f"_LoggerOutput id '{output}' was not found")

        raise TypeError(
            "output must be a pawprints._LoggerOutput or int matching a _LoggerOutput's id"
        )

    def remove_output(self, arg, /):
        """
        Remove a logger output from this Logger.

        :param output: Logger output to remove
        :type output: _LoggerOutput
        :param id: ID of the output to remove
        :type id: int
        """

        if isinstance(arg, _LoggerOutput):
            if arg in self.__outputs:
                self.__outputs.remove(arg)

        elif isinstance(arg, int):
            if output_object := _outputs.get(arg, None):
                if output_object in self.__outputs:
                    self.__outputs.remove(output_object)

        else:
            raise TypeError(
                "output to remove must be a pawprints._LoggerOutput or an int"
            )

    def clear_outputs(self):
        """
        Clear (remove) all logger outputs from this Logger.
        """

        self.__outputs = []

    @property
    def name(self):
        """
        The name of this Logger.
        """

        return self.__name

    @property
    def formatter(self):
        """
        This Logger's Formatter.
        """

        return self.__formatter

    @formatter.setter
    def formatter(self, new):
        if not isinstance(new, Formatter):
            raise TypeError("formatter must be a pawprints.Formatter")

        self.__formatter = new

    @property
    def outputs(self):
        """
        The logger outputs this Logger outputs logs to.

        :return: A list of all of this Logger's logger outputs
        :rtype: List[_LoggerOutput]
        """

        return self.__outputs

    @property
    def id(self):
        """
        The id of the logger.
        A logger's id shows its place in the order of creation.
        Logger ids start at 0 and grow by 1 for each new logger.
        Logger id 0 is by default occupied by the root Logger.
        """

        return self.__id

    @property
    def level(self):
        """
        The logging level being used by this Logger.
        """

        return get_level_name(self.__level)

    @level.setter
    def level(self, new):
        level = get_level(new)
        if level is None:
            raise ValueError("level must be a valid logging level (1-7)")

        self.__level = new

    @property
    def levelno(self):
        """
        The logging level name being used by this Logger.
        """

        return self.__level

    @property
    def enabled(self):
        """
        Whether the logger is currently enabled.
        """

        return self.__enabled

    @enabled.setter
    def enabled(self, new):
        if not isinstance(new, bool):
            raise TypeError("enabled must be a bool")

        self.__enabled = new


root = Logger("root", INFO)
root.add_output(StreamOutput())


def config_root(
    *, level=None, formatter=None, outputs=None, enabled=None, filepath=None
):
    """
    Configure the root Logger.
    Leave values as None to leave them unchanged.

    :param level: Lowest logging level to track, defaults to None
    :type level: int | str | None, optional
    :param formatter: Formatter to use, defaults to None
    :type formatter: pawprints.Formatter | None, optional
    :param outputs: An iterable of outputs to use, defaults to None
    :type outputs: Sequence[_LoggerOutput] | None, optional
    :param enabled: Whether to enable the root Logger, defaults to None
    :type enabled: bool | None, optional
    :param filepath: A filepath that will be used to create a
    FileOutput connected to the root Logger, defaults to None
    :type filepath: str | None, optional
    """

    # We don't need to type check most kwargs here since it's
    # already done in all of these setter methods.

    if level is not None:
        root.level = level
    if formatter is not None:
        root.formatter = formatter
    if outputs is not None:
        root.clear_outputs()
        for output in outputs:
            root.add_output(output)
    if enabled is not None:
        root.enabled = enabled
    if filepath is not None:
        if not isinstance(filepath, str):
            raise TypeError("filepath must be a str")

        for output in root.outputs:
            if isinstance(output, FileOutput):
                root.remove_output(output)
        root.add_output(FileOutput(filepath))

    if len(root.outputs) == 0:
        root.add_output(StreamOutput())


def reset_root():
    """
    Reset the root Logger's config.
    """

    root.level = INFO
    root.formatter = default_formatter
    root.clear_outputs()
    root.add_output(StreamOutput())
    root.enabled = True


def log(message, level=NO_LEVEL_SET, /):
    """
    Create a log with the given message and level.
    If level is left as NO_LEVEL_SET, it will default to this Logger's set level.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    :param level: Logging level to use, defaults to NO_LEVEL_SET
    :type level: int | str | pawprints._NoLogLevelSentinel, optional
    """

    if level == NO_LEVEL_SET:
        level = root.level

    root.log(message, level)


def debug(message, /):
    """
    Create a DEBUG level log with the given message.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    """

    root.log(message, DEBUG)


def command_call(message, /):
    """
    Create a CMD_CALL level log with the given message.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    """

    root.log(message, CMD_CALL)


cmd_call = command_call


def info(message, /):
    """
    Create an INFO level log with the given message.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    """

    root.log(message, INFO)


def setup(message, /):
    """
    Create a SETUP level log with the given message.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    """

    root.log(message, SETUP)


def warning(message, /):
    """
    Create a WARNING level log with the given message.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    """

    root.log(message, WARNING)


warn = warning


def error(message, /):
    """
    Create an ERROR level log with the given message.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    """

    root.log(message, ERROR)


def fatal(message, /):
    """
    Create a FATAL level log with the given message.

    :param message: Message to log
    :type message: SupportsStr | SupportsRepr
    """

    root.log(message, FATAL)
