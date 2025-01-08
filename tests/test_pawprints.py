# pylint: disable=all

from datetime import datetime
from io import StringIO
from inspect import stack
from os import remove
from time import time

import pytest

from CatBot.CatBot_utils import pawprints


def test_root_logging_config():
    pawprints.config_root(level=pawprints.DEBUG, enabled=False)
    assert pawprints.root.level == "DEBUG"
    assert pawprints.root.enabled is False
    pawprints.reset_root()
    assert pawprints.root.level == "INFO"
    assert pawprints.root.enabled is True


def test_root_logging_functions():
    pawprints.reset_root()

    logging_funcs = (
        pawprints.debug,
        pawprints.command_call,
        pawprints.cmd_call,
        pawprints.info,
        pawprints.setup,
        pawprints.warn,
        pawprints.warning,
        pawprints.error,
        pawprints.fatal,
    )
    out_stream = StringIO()
    pawprints.config_root(
        level=pawprints.DEBUG, outputs=[pawprints.StreamOutput(out_stream)]
    )

    for log_func in logging_funcs:
        log_func(f"{log_func.__name__} test")
        output = out_stream.getvalue()
        assert (
            f"{log_func.__name__} test" in output
        ), f"Failed for {log_func.__name__}, got: {repr(output)}"


def test_file_output():
    pawprints.reset_root()

    file_output = pawprints.FileOutput("log_file.log")

    pawprints.config_root(outputs=[file_output])
    pawprints.info("file logging test")

    with open("log_file.log", encoding="utf8") as file:
        assert "file logging test" in file.read()

    remove("log_file.log")

    assert file_output.encoding is None
    assert file_output.errors is None
    assert file_output.filepath == "log_file.log"
    assert file_output.open_text_mode == "a"


def test_formatter():
    pawprints.reset_root()

    formatter = pawprints.Formatter(pawprints.DEFAULT_FORMAT)

    assert formatter.end == "\n"
    assert formatter.template == pawprints.DEFAULT_FORMAT
    assert formatter.timestamp_format == pawprints.DEFAULT_TIMESTAMP_FORMAT

    formatter.template = "{message} {ftime}"
    formatter.timestamp_format = "%Y"
    stream = StringIO()
    pawprints.config_root(formatter=formatter, outputs=[pawprints.StreamOutput(stream)])

    pawprints.info("formatter testing")

    assert f"formatter testing {datetime.now().year}\n" == stream.getvalue()


def test_get_level():
    assert pawprints.get_level(1) == 1
    assert pawprints.get_level(2) == 2
    assert pawprints.get_level(3) == 3
    assert pawprints.get_level(4) == 4
    assert pawprints.get_level(5) == 5
    assert pawprints.get_level(6) == 6
    assert pawprints.get_level(7) == 7
    assert pawprints.get_level("DEBUG") == 1
    assert pawprints.get_level("COMMAND_CALL") == 2
    assert pawprints.get_level("CMD_CALL") == 2
    assert pawprints.get_level("INFO") == 3
    assert pawprints.get_level("SETUP") == 4
    assert pawprints.get_level("WARNING") == 5
    assert pawprints.get_level("WARN") == 5
    assert pawprints.get_level("ERROR") == 6
    assert pawprints.get_level("FATAL") == 7


def test_get_level_name():
    assert pawprints.get_level_name(1) == "DEBUG"
    assert pawprints.get_level_name(2) == "COMMAND_CALL"
    assert pawprints.get_level_name(3) == "INFO"
    assert pawprints.get_level_name(4) == "SETUP"
    assert pawprints.get_level_name(5) == "WARNING"
    assert pawprints.get_level_name(6) == "ERROR"
    assert pawprints.get_level_name(7) == "FATAL"
    assert pawprints.get_level_name("DEBUG") == "DEBUG"
    assert pawprints.get_level_name("COMMAND_CALL") == "COMMAND_CALL"
    assert pawprints.get_level_name("CMD_CALL") == "CMD_CALL"
    assert pawprints.get_level_name("INFO") == "INFO"
    assert pawprints.get_level_name("SETUP") == "SETUP"
    assert pawprints.get_level_name("WARNING") == "WARNING"
    assert pawprints.get_level_name("WARN") == "WARN"
    assert pawprints.get_level_name("ERROR") == "ERROR"
    assert pawprints.get_level_name("FATAL") == "FATAL"


def test_get_logger():
    pawprints.reset_root()

    assert pawprints.get_logger(0) == pawprints.root
    assert pawprints.get_logger("root") == pawprints.root
    assert pawprints.get_logger(0, "root") == pawprints.root
    assert pawprints.get_logger(1) == None
    assert pawprints.get_logger("secondary") == None
    assert pawprints.get_logger(1, "secondary") == None


def test_logger():
    logger = pawprints.Logger("secondary", pawprints.INFO)
    formatter = pawprints.Formatter("{message}")
    stream_output = pawprints.StreamOutput()
    file_output = pawprints.FileOutput("log_file.log")

    assert logger.name == "secondary"
    assert logger.formatter == pawprints.default_formatter
    logger.formatter = formatter
    assert logger.formatter == formatter
    assert logger.outputs == []
    logger.add_output(stream_output)
    logger.add_output(file_output)
    assert logger.outputs == [stream_output, file_output]
    logger.remove_output(stream_output)
    assert logger.outputs == [file_output]
    logger.remove_output(file_output.id)
    assert logger.outputs == []
    logger.add_output(stream_output)
    logger.add_output(file_output)
    logger.clear_outputs()
    assert logger.outputs == []
    assert logger.id == 1
    assert logger.level == "INFO"
    assert logger.levelno == 3
    logger.level = pawprints.DEBUG
    assert logger.level == "DEBUG"
    assert logger.levelno == 1
    assert logger.enabled is True
    logger.enabled = False
    assert logger.enabled is False


def test_log_message():
    log_msg = pawprints.LogMessage(
        "Something is wrong!", pawprints.FATAL, "root", stack()[0]
    )
    current_time = time()

    assert log_msg.filename == "test_pawprints.py"
    # We don't test full filepath here since it will vary from machine to machine.
    assert log_msg.filepath.endswith("test_pawprints.py")
    assert log_msg.level == "FATAL"
    assert log_msg.levelno == 7
    # Update this to whatever lineno the line containing
    # "Something is wrong!", pawprints.FATAL, "root", stack()[0]
    # has if test fails here.
    assert log_msg.lineno == 172
    assert log_msg.logger_name == "root"
    assert log_msg.message == "Something is wrong!"
    assert log_msg.module == "test_pawprints"
    assert log_msg.time == current_time


if __name__ == "__main__":
    pytest.main()
