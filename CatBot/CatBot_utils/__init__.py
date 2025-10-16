"""
CatBot_utils
Package containing various utility functions for CatBot's internal workings.
"""

# pylint: disable=invalid-name

from . import emojis
from .bot_init import (
    CAT_API_SEARCH_LINK,
    LOG_FILE,
    LOGGING_CHANNEL,
    MANAGEMENT_ROLES,
    MODERATOR_ROLES,
    VERSION,
    config_logging,
    get_token,
    handle_app_command_error,
    initialize_bot,
    initialize_cli_arg_parser,
)
from .confirm_button import ConfirmButton
from .internal_utils import (
    DEFAULT_EMBED_COLOR,
    START_TIME,
    TIME_MULTIPLICATION_TABLE,
    TimeUnit,
    generate_authored_embed_with_icon,
    wrap_reason,
)
