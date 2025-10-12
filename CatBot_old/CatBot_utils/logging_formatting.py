"""
logging_formatting.py
Logging formatting code.
"""

from . import pawprints


class ColorFormatter(pawprints.Formatter):
    """
    Custom color formatter for logging stream outputs.
    """

    DEBUG = "\x1b[32m"  # green
    CALL = "\x1b[36m"  # light blue
    INFO = "\x1b[34m"  # blue
    SETUP = "\x1b[35m"  # magenta
    WARNING = "\x1b[33m"  # yellow
    ERROR = "\x1b[31m"  # red
    FATAL = "\x1b[31m" + "\x1b[1m"  # red in bold
    RESET = "\x1b[0m"

    def get_format_by_level(self, levelno: int, /) -> str:
        """
        Get the format to use based on the levelno.

        :param levelno: Logging level
        :type levelno: int
        :return: Format to use for the given levelno
        :rtype: str
        """

        formats = {
            pawprints.DEBUG: self.DEBUG + self.template + self.RESET,
            pawprints.CALL: self.CALL + self.template + self.RESET,
            pawprints.INFO: self.INFO + self.template + self.RESET,
            pawprints.SETUP: self.SETUP + self.template + self.RESET,
            pawprints.WARNING: self.WARNING + self.template + self.RESET,
            pawprints.ERROR: self.ERROR + self.template + self.RESET,
            pawprints.FATAL: self.FATAL + self.template + self.RESET,
        }

        return formats[levelno]

    def format(self, message: pawprints.LogMessage, /) -> str:
        """
        Apply the format to the log message.

        :param message: Logging message
        :type message: pawprints.LogMessage
        :return: Formatted log
        :rtype: str
        """

        formatter = pawprints.Formatter(self.get_format_by_level(message.levelno))
        return formatter.format(message)
