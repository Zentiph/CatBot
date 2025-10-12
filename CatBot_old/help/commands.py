"""
commands.py
Contains definitions of commands to be used with the /help command.
"""

# pylint: disable=too-many-lines

from typing import Literal, Union

from discord import Member, Role, TextChannel, User

from ..CatBot_utils import TimeUnit
from ..date_time import Month
from .representations import Command, Param

HelpCategory = Literal["color", "date-time", "fun", "help", "math", "random", "stats"]
ClassifiedHelpCategory = Literal["management", "moderation"]


# # # # # # # #
# COLORS CMDS #
# # # # # # # #

color_role_hex = Command(
    name="color role hex",
    description="Assign yourself a custom color role with a hex value.",
)
color_role_hex.add_param(
    Param(name="hex", type=str, description="Hex value (#000000-#ffffff)")
)

color_role_rgb = Command(
    name="color role rgb",
    description="Assign yourself a custom color role with an RGB value.",
)
color_role_rgb.add_param(Param(name="r", type=int, description="Red value (0-255)"))
color_role_rgb.add_param(Param(name="g", type=int, description="Green value (0-255)"))
color_role_rgb.add_param(Param(name="b", type=int, description="Blue value (0-255)"))

color_role_name = Command(
    name="color role name",
    description="Assign yourself a custom color role with a color name.",
)
color_role_name.add_param(
    Param(
        name="name",
        type=str,
        description="Color name (use /colors for a list of allowed colors)",
    )
)

color_role_random = Command(
    name="color role random",
    description="Assign yourself a custom color role with a randomly generated color.",
)
color_role_random.add_param(
    Param(
        name="seed",
        type=Union[str, None],
        description="Optional seed to use when generating the random color",
        optional=True,
    )
)

color_role_copy_color = Command(
    name="color role copy-color",
    description="Assign yourself a custom color role by copying another role's color.",
)
color_role_copy_color.add_param(
    Param(name="role", type=Role, description="Role to copy the color of")
)

color_role_reset = Command(
    name="color role reset",
    description="Reset your color role's color to the default Discord color (invisible, #000000).",
)

color_role_reassign = Command(
    name="color role reassign",
    description="Check if you are missing your color role, "
    + "and reassign it if so and the role exists.",
)

color_color_list = Command(
    name="color color-list",
    description="Provides a list of all allowed color names used with CatBot.",
)
color_color_list.add_param(
    Param(
        name="group",
        type=Literal[
            "red",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "pink",
            "brown",
            "white",
            "gray",
            "grey",
        ],
        description="Group of colors to get the allowed names of",
    )
)

color_info_rgb = Command(
    name="color info rgb",
    description="Get information about an RGB color, "
    + "such as its hex equivalent and its color name equivalent, "
    + "if available, and an image preview.",
)
color_info_rgb.add_param(Param(name="r", type=int, description="Red value (0-255)"))
color_info_rgb.add_param(Param(name="g", type=int, description="Green value (0-255)"))
color_info_rgb.add_param(Param(name="b", type=int, description="Blue value (0-255)"))

color_info_hex = Command(
    name="color info hex",
    description="Get information about a hex color, "
    + "such as its RGB equivalent and its color name equivalent, "
    + "if available, and an image preview.",
)
color_info_hex.add_param(
    Param(name="hex", type=str, description="Hex value (#000000-#ffffff)")
)

color_info_name = Command(
    name="color info name",
    description="Get information about a color name, "
    + "such as its hex and RGB equivalents and its color name equivalent, "
    + "if available, and an image preview.",
)
color_info_name.add_param(
    Param(
        name="name",
        type=str,
        description="Color name (use /colors for a list of allowed colors)",
    )
)

color_info_role = Command(
    name="color info role",
    description="Get information about a role's color, "
    + "such as its hex and RGB equivalents and its color name equivalent, "
    + "if available, and an image preview.",
)
color_info_role.add_param(
    Param(name="role", type=Role, description="Role to get the color information of")
)

color_random = Command(name="color random", description="Generate a random color.")
color_random.add_param(
    Param(
        name="seed",
        type=Union[str, None],
        description="Optional seed to use when generating the random color",
        optional=True,
    )
)

color_invert_rgb = Command(name="color invert rgb", description="Invert an RGB color.")
color_invert_rgb.add_param(Param(name="r", type=int, description="Red value (0-255)"))
color_invert_rgb.add_param(Param(name="g", type=int, description="Green value (0-255)"))
color_invert_rgb.add_param(Param(name="b", type=int, description="Blue value (0-255)"))

color_invert_hex = Command(name="color invert hex", description="Invert a hex color.")
color_invert_hex.add_param(
    Param(name="hex", type=str, description="Hex value (#000000-#ffffff)")
)

color_invert_name = Command(
    name="color invert name", description="Invert a color name."
)
color_invert_name.add_param(
    Param(
        name="name",
        type=str,
        description="Color name (use /colors for a list of allowed colors)",
    )
)

# # # # # # # # #
# DATETIME CMDS #
# # # # # # # # #

date_time_date_time = Command(
    name="date-time date-time", description="Get the date and time in a timezone"
)
date_time_date_time.add_param(
    Param(
        name="timezone",
        type=str,
        description="The timezone to get the date and time in",
    )
)
date_time_date_time.add_param(
    Param(
        name="military_time",
        type=bool,
        description="Whether to use military (24-hour) time",
        default=False,
    )
)
date_time_date_time.add_param(
    Param(
        name="seconds",
        type=bool,
        description="Whether to include seconds in the time",
        default=False,
    )
)
date_time_date_time.add_param(
    Param(
        name="microseconds",
        type=bool,
        description="Whether to include microseconds in the time "
        + "(if True, seconds are included too)",
        default=False,
    )
)

date_time_date = Command(
    name="date-time date", description="Get the date in a timezone"
)
date_time_date.add_param(
    Param(name="timezone", type=str, description="The timezone to get the date in")
)

date_time_time = Command(
    name="date-time time", description="Get the time in a timezone"
)
date_time_time.add_param(
    Param(name="timezone", type=str, description="The timezone to get the time in")
)
date_time_time.add_param(
    Param(
        name="military_time",
        type=bool,
        description="Whether to use military (24-hour) time",
        default=False,
    )
)
date_time_time.add_param(
    Param(
        name="seconds",
        type=bool,
        description="Whether to include seconds in the time",
        default=False,
    )
)
date_time_time.add_param(
    Param(
        name="microseconds",
        type=bool,
        description="Whether to include microseconds in the time "
        + "(if True, seconds are included too)",
        default=False,
    )
)

date_time_weekday = Command(
    name="date-time weekday", description="Get the weekday of a given date"
)
date_time_weekday.add_param(
    Param(name="month", type=Month, description="The month of the year")
)
date_time_weekday.add_param(
    Param(name="day", type=int, description="The day of the month")
)
date_time_weekday.add_param(Param(name="year", type=int, description="The year"))

date_time_days_until = Command(
    name="date-time days-until", description="Find how many days are until a given date"
)
date_time_days_until.add_param(
    Param(name="month", type=Month, description="Month of the year")
)
date_time_days_until.add_param(
    Param(name="day", type=int, description="Day of the month")
)
date_time_days_until.add_param(Param(name="year", type=int, description="Year"))

# # # # # # # # #
# FUN/MISC CMDS #
# # # # # # # # #

flip_coin = Command(name="flip-coin", description="Flip a coin")

bot_stats = Command(name="bot-stats", description="Get statistics about myself, CatBot")

profile_picture = Command(
    name="profile-picture", description="Get a user's profile picture"
)
profile_picture.add_param(
    Param(
        name="user",
        type=User,
        description="The user to get the profile picture of (gets yours if left empty)",
        optional=True,
    )
)

banner = Command(name="banner", description="Get a user's profile banner")
banner.add_param(
    Param(
        name="user",
        type=User,
        description="The user to get the profile banner of (gets yours if left empty)",
        optional=True,
    )
)

cat_pic = Command(name="cat-pic", description="Get a random cat picture")

member_count = Command(
    name="member-count", description="Get a count of the members in this server"
)


# # # # # # #
# HELP CMDS #
# # # # # # #

help_category = Command(
    name="help category",
    description="List information about all the commands in a category",
)
help_category.add_param(
    Param(
        name="category",
        type=HelpCategory,
        description="Command category to get help for",
    )
)

help_command = Command(
    name="help command", description="Get help for a specific command."
)
help_command.add_param(
    Param(name="cmd", type=str, description="Command to get help for")
)

# # # # # # # # # #
# MANAGEMENT CMDS #
# # # # # # # # # #

mgmt_echo = Command(name="mgmt echo", description="Echo a message back to a channel.")
mgmt_echo.add_param(Param(name="message", type=str, description="Message to echo"))
mgmt_echo.add_param(
    Param(
        name="channel",
        type=Union[TextChannel, None],
        description="Channel to send the echoed message to; defaults to current channel if empty",
    )
)

mgmt_dm = Command(name="mgmt dm", description="Send a direct message to a user.")
mgmt_dm.add_param(
    Param(name="user", type=User, description="User to send the direct message to")
)
mgmt_dm.add_param(
    Param(name="message", type=str, description="Message to send to the user")
)

mgmt_announce = Command(
    name="mgmt announce", description="Announce a message to a channel."
)
mgmt_announce.add_param(
    Param(name="message", type=str, description="Message to announce")
)
mgmt_announce.add_param(
    Param(
        name="channel",
        type=Union[TextChannel, None],
        description="Channel to send the announced message to; "
        + "defaults to current channel if empty",
    )
)
mgmt_announce.add_param(
    Param(
        name="ping",
        type=Role,
        description="Role to ping for the announcement, or no ping if left empty",
        optional=True,
    )
)

# # # # # # #
# MATH CMDS #
# # # # # # #

math_add = Command(name="math add", description="Add two numbers.")
math_add.add_param(Param(name="x", type=float, description="First number"))
math_add.add_param(Param(name="y", type=float, description="Second number"))
math_add.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_sum = Command(
    name="math sum", description="Calculate the sum of an arbitrary amount of numbers."
)
math_sum.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to sum, separated by commas (e.g. "1,2,3")',
    )
)
math_sum.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_sub = Command(name="math sub", description="Subtract two numbers.")
math_sub.add_param(Param(name="x", type=float, description="First number"))
math_sub.add_param(Param(name="y", type=float, description="Second number"))
math_sub.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_mul = Command(name="math mul", description="Multiply two numbers.")
math_mul.add_param(Param(name="x", type=float, description="First number"))
math_mul.add_param(Param(name="y", type=float, description="Second number"))
math_mul.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_prod = Command(
    name="math prod",
    description="Calculate the product of an arbitrary amount of numbers.",
)
math_prod.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to find the product of, separated by commas (e.g. "1,2,3")',
    )
)
math_prod.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_div = Command(name="math div", description="Divide two numbers.")
math_div.add_param(Param(name="x", type=float, description="First number"))
math_div.add_param(Param(name="y", type=float, description="Second number"))
math_div.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_floordiv = Command(
    name="math floordiv", description="Divide two numbers and floor it."
)
math_floordiv.add_param(Param(name="x", type=float, description="First number"))
math_floordiv.add_param(Param(name="y", type=float, description="Second number"))

math_pow = Command(
    name="math pow", description="Raise a number to the power of another."
)
math_pow.add_param(Param(name="x", type=float, description="First number"))
math_pow.add_param(Param(name="y", type=float, description="Second number"))
math_pow.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_mod = Command(name="math mod", description="Calculate the modulus of two numbers.")
math_mod.add_param(Param(name="x", type=float, description="First number"))
math_mod.add_param(Param(name="y", type=float, description="Second number"))

math_sqrt = Command(
    name="math sqrt", description="Calculate the square root of a number."
)
math_sqrt.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the square root of",
    )
)
math_sqrt.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_cbrt = Command(
    name="math cbrt", description="Calculate the cube root of a number."
)
math_cbrt.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the cube root of",
    )
)
math_cbrt.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_nroot = Command(
    name="math nroot", description="Calculate the nth root of a number."
)
math_nroot.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the nth root of",
    )
)
math_nroot.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_abs = Command(
    name="math abs", description="Calculate the absolute value of a number."
)
math_abs.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the absolute value of",
    )
)

math_ceil = Command(name="math ceil", description="Calculate the ceiling of a number.")
math_ceil.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the ceiling of",
    )
)

math_floor = Command(name="math floor", description="Calculate the floor of a number.")
math_floor.add_param(
    Param(name="x", type=float, description="Number to calculate the floor of")
)

math_round = Command(
    name="math round", description="Round a number to a specified number of digits."
)
math_round.add_param(Param(name="x", type=float, description="Number to round"))
math_round.add_param(
    Param(name="ndigits", type=int, description="Number of digits to round to")
)

math_log = Command(name="math log", description="Calculate the logarithm of a number.")
math_log.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the logarithm of",
    )
)
math_log.add_param(
    Param(
        name="base",
        type=Union[float, None],
        description="Base of the logarithm",
        default=10,
    )
)
math_log.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_ln = Command(
    name="math ln", description="Calculate the natural logarithm of a number."
)
math_ln.add_param(
    Param(
        name="x", type=float, description="Number to calculate the natural logarithm of"
    )
)
math_ln.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_gcd = Command(
    name="math gcd",
    description="Calculate the greatest common divisor/denominator (GDC) of two numbers",
)
math_gcd.add_param(Param(name="x", type=int, description="First number"))
math_gcd.add_param(Param(name="y", type=int, description="Second number"))

math_gcd_bulk = Command(
    name="math gcd-bulk",
    description="Calculate the GCD of an arbitrary amount of numbers.",
)
math_gcd_bulk.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to find the GCD of, separated by commas (e.g. "1,2,3")',
    )
)

math_lcm = Command(
    name="math lcm",
    description="Calculate the least common multiplier (LCM) of two numbers.",
)
math_lcm.add_param(Param(name="x", type=int, description="First number"))
math_lcm.add_param(Param(name="y", type=int, description="Second number"))

math_lcm_bulk = Command(
    name="math lcm-bulk",
    description="Calculate the LCM of an arbitrary amount of numbers.",
)
math_lcm_bulk.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to find the LCM of, separated by commas (e.g. "1,2,3")',
    )
)

math_distance_cartesian_2d = Command(
    name="math distance cartesian-2d",
    description="Calculate the Cartesian distance between two points in 2D space.",
)
math_distance_cartesian_2d.add_param(
    Param(name="x1", type=float, description="First x-coordinate")
)
math_distance_cartesian_2d.add_param(
    Param(name="y1", type=float, description="First y-coordinate")
)
math_distance_cartesian_2d.add_param(
    Param(name="x2", type=float, description="Second x-coordinate")
)
math_distance_cartesian_2d.add_param(
    Param(name="y2", type=float, description="Second y-coordinate")
)
math_distance_cartesian_2d.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_distance_cartesian_3d = Command(
    name="math distance cartesian-3d",
    description="Calculate the Cartesian distance between two points in 3D space.",
)
math_distance_cartesian_3d.add_param(
    Param(name="x1", type=float, description="First x-coordinate")
)
math_distance_cartesian_3d.add_param(
    Param(name="y1", type=float, description="First y-coordinate")
)
math_distance_cartesian_3d.add_param(
    Param(name="z1", type=float, description="First z-coordinate")
)
math_distance_cartesian_3d.add_param(
    Param(name="x2", type=float, description="Second x-coordinate")
)
math_distance_cartesian_3d.add_param(
    Param(name="y2", type=float, description="Second y-coordinate")
)
math_distance_cartesian_3d.add_param(
    Param(name="z2", type=float, description="Second z-coordinate")
)
math_distance_cartesian_3d.add_param(
    Param(
        name="ndigits",
        type=int,
        description="Number of digits to round the result to",
        optional=False,
        default=10,
    )
)

math_factorial = Command(
    name="math factorial", description="Calculate the factorial of a number."
)
math_factorial.add_param(
    Param(name="x", type=int, description="Number to calculate the factorial of")
)

# # # # # # # # # #
# MODERATION CMDS #
# # # # # # # # # #

mod_ban = Command(name="mod ban", description="Ban a user.")
mod_ban.add_param(Param(name="user", type=User, description="User to ban"))
mod_ban.add_param(
    Param(
        name="delete_message_time",
        type=int,
        description="How much of the user's message history to delete",
        default=0,
    )
)
mod_ban.add_param(
    Param(
        name="time_unit",
        type=TimeUnit,
        description="Unit of time",
        default="seconds",
    )
)
mod_ban.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Ban reason",
        optional=True,
    )
)
mod_ban.add_param(
    Param(
        name="ghost",
        type=bool,
        description="Don't notify the user",
        default=False,
    )
)

mod_unban = Command(name="mod unban", description="Unban a user.")
mod_unban.add_param(
    Param(name="user_id", type=str, description="ID of the user to unban")
)
mod_unban.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Unban reason",
        optional=True,
    )
)

mod_timeout_add = Command(
    name="mod timeout add", description="Add time to a user's timeout."
)
mod_timeout_add.add_param(
    Param(name="user", type=Member, description="User to add timeout time to")
)
mod_timeout_add.add_param(
    Param(name="time", type=int, description="Timeout addition time")
)
mod_timeout_add.add_param(
    Param(
        name="time_unit",
        type=TimeUnit,
        description="Unit of time",
        default="seconds",
    )
)
mod_timeout_add.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Timeout addition reason",
        optional=True,
    )
)

mod_timeout_reduce = Command(
    name="mod timeout reduce", description="Reduce time from a user's timeout."
)
mod_timeout_reduce.add_param(
    Param(name="user", type=Member, description="User to reduce timeout time from")
)
mod_timeout_reduce.add_param(
    Param(name="time", type=int, description="Timeout reduction time")
)
mod_timeout_reduce.add_param(
    Param(
        name="time_unit",
        type=TimeUnit,
        description="Unit of time",
        default="seconds",
    )
)
mod_timeout_reduce.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Timeout reduction reason",
        optional=True,
    )
)

mod_timeout_remove = Command(
    name="mod timeout remove", description="Remove a user's timeout."
)
mod_timeout_remove.add_param(
    Param(name="user", type=Member, description="User to remove timeout from")
)
mod_timeout_remove.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Timeout removal reason",
        optional=True,
    )
)

mod_clear = Command(
    name="mod clear", description="Delete a number of messages from a channel."
)
mod_clear.add_param(
    Param(name="amount", type=int, description="Number of messages to delete")
)
mod_clear.add_param(
    Param(
        name="channel",
        type=Union[TextChannel, None],
        description="Channel to delete messages from; defaults to current channel if empty",
        optional=True,
    )
)
mod_clear.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Deletion reason",
        optional=True,
    )
)

mod_warn = Command(name="mod warn", description="Warn a user.")
mod_warn.add_param(Param(name="user", type=Member, description="User to warn"))
mod_warn.add_param(
    Param(
        name="channel", type=TextChannel, description="Channel to send the warning in"
    )
)
mod_warn.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Warning reason",
        optional=True,
    )
)

mod_kick = Command(name="mod kick", description="Kick a user.")
mod_kick.add_param(Param(name="user", type=Member, description="User to kick"))
mod_kick.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Kick reason",
        optional=True,
    )
)

mod_mute = Command(name="mod mute", description="Mute a user.")
mod_mute.add_param(Param(name="user", type=Member, description="User to mute"))
mod_mute.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Mute reason",
        optional=True,
    )
)

mod_unmute = Command(name="mod unmute", description="Unmute a user.")
mod_unmute.add_param(Param(name="user", type=Member, description="User to unmute"))
mod_unmute.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Unmute reason",
        optional=True,
    )
)

# # # # # # # #
# RANDOM CMDS #
# # # # # # # #

random_integer = Command(
    name="random integer",
    description="Generate a random integer within a specified range, [a, b]",
)
random_integer.add_param(
    Param(
        name="a",
        type=int,
        description="The left endpoint (inclusive)",
        default=0,
    )
)
random_integer.add_param(
    Param(
        name="b",
        type=int,
        description="The right endpoint (inclusive)",
        default=10,
    )
)
random_integer.add_param(
    Param(
        name="seed",
        type=str,
        description="Optional seed to use when generating the value",
        optional=True,
    )
)

random_decimal = Command(
    name="random decimal",
    description="Generate a random decimal number (float) within a specified range, [a, b]",
)
random_decimal.add_param(
    Param(
        name="a",
        type=float,
        description="The left endpoint (inclusive)",
        default=0.0,
    )
)
random_decimal.add_param(
    Param(
        name="b",
        type=float,
        description="The right endpoint (inclusive)",
        default=1.0,
    )
)
random_decimal.add_param(
    Param(
        name="seed",
        type=str,
        description="Optional seed to use when generating the value",
        optional=True,
    )
)

random_choice = Command(
    name="random choice",
    description="Randomly choose a value from a list of values",
)
random_choice.add_param(
    Param(
        name="values",
        type=str,
        description='A list of values separated by commas (e.g. "1,2,3,a,b,c")',
    )
)
random_choice.add_param(
    Param(
        name="choices",
        type=int,
        description="The number of choices to pick from the given values",
        default=1,
    )
)
random_choice.add_param(
    Param(
        name="duplicates",
        type=bool,
        description="Whether the same choice can be made multiple times",
        default=True,
    )
)
random_choice.add_param(
    Param(
        name="seed",
        type=str,
        description="Optional seed to use when generating the value(s)",
        optional=True,
    )
)

random_shuffle = Command(
    name="random shuffle", description="Shuffle a list of values randomly"
)
random_shuffle.add_param(
    Param(
        name="values",
        type=str,
        description='A list of values separated by commas (e.g. "1,2,3,a,b,cat")',
    )
)
random_shuffle.add_param(
    Param(
        name="seed",
        type=str,
        description="Optional seed to use when generating the value",
        optional=True,
    )
)

# # # # # # # # # #
# STATISTICS CMDS #
# # # # # # # # # #

stats_mean = Command(
    name="/stats mean", description="Compute the mean (average value) of a data set"
)
stats_mean.add_param(
    Param(
        name="numbers",
        type=str,
        description='A list of numbers separated by commas (e.g. "1,2,3,4"',
    )
)

stats_median = Command(
    name="/stats median",
    description="Compute the median (middle value) of a data set; "
    + "the median will be calculated as the average of the two "
    + "middle values if there are an even amount of values",
)
stats_median.add_param(
    Param(
        name="numbers",
        type=str,
        description='A list of numbers separated by commas (e.g. "1,2,3,4"',
    )
)

stats_mode = Command(
    name="/stats mode",
    description="Compute the mode (most occurring value) of a data set; "
    + "if there are multiple modes, the first occurring mode will be returned; "
    + "see /stats multimode for calculating multiple modes",
)
stats_mode.add_param(
    Param(
        name="numbers",
        type=str,
        description='A list of numbers separated by commas (e.g. "1,2,3,4"',
    )
)

stats_multimode = Command(
    name="/stats multimode",
    description="Compute all the modes (most occurring values) of a data set",
)
stats_multimode.add_param(
    Param(
        name="numbers",
        type=str,
        description='A list of numbers separated by commas (e.g. "1,2,3,4"',
    )
)


# # # # # # # # #
# CMD LIST INIT #
# # # # # # # # #

COLOR = (
    color_role_hex,
    color_role_rgb,
    color_role_name,
    color_role_random,
    color_role_copy_color,
    color_role_reset,
    color_role_reassign,
    color_color_list,
    color_info_rgb,
    color_info_hex,
    color_info_name,
    color_info_role,
    color_random,
    color_invert_rgb,
    color_invert_hex,
    color_invert_name,
)
DATETIME = (
    date_time_date_time,
    date_time_date,
    date_time_time,
    date_time_weekday,
    date_time_days_until,
)
FUN = (flip_coin, bot_stats, profile_picture, banner, cat_pic, member_count)
HELP = (help_category, help_command)
MATH = (
    math_add,
    math_sum,
    math_sub,
    math_mul,
    math_prod,
    math_div,
    math_floordiv,
    math_pow,
    math_mod,
    math_sqrt,
    math_cbrt,
    math_nroot,
    math_abs,
    math_ceil,
    math_floor,
    math_round,
    math_log,
    math_ln,
    math_gcd,
    math_gcd_bulk,
    math_lcm,
    math_lcm_bulk,
    math_distance_cartesian_2d,
    math_distance_cartesian_3d,
    math_factorial,
)
RANDOM = (random_integer, random_decimal, random_choice, random_shuffle)
STATS = (stats_mean, stats_median, stats_mode, stats_mode, stats_multimode)

MANAGEMENT = (mgmt_echo, mgmt_dm, mgmt_announce)
MODERATION = (
    mod_ban,
    mod_timeout_add,
    mod_timeout_reduce,
    mod_timeout_remove,
    mod_clear,
    mod_warn,
    mod_kick,
    mod_mute,
    mod_unmute,
)


PUBLIC = COLOR + DATETIME + FUN + HELP + MATH + RANDOM + STATS
PUBLIC_COMMAND_MAP = {
    # COLOR CMDS
    "color role hex": color_role_hex,
    "color role rgb": color_role_rgb,
    "color role name": color_role_name,
    "color role random": color_role_random,
    "color role copy-color": color_role_copy_color,
    "color role reset": color_role_reset,
    "color role reassign": color_role_reassign,
    "color color-list": color_color_list,
    "color info rgb": color_info_rgb,
    "color info hex": color_info_hex,
    "color info name": color_info_name,
    "color info role": color_info_role,
    "color random": color_random,
    "color invert rgb": color_invert_rgb,
    "color invert hex": color_invert_hex,
    "color invert name": color_invert_name,
    # DATETIME CMDS
    "date-time date-time": date_time_date_time,
    "date-time date": date_time_date,
    "date-time time": date_time_time,
    "date-time weekday": date_time_weekday,
    "date-time days-until": date_time_days_until,
    # FUN CMDS
    "flip-coin": flip_coin,
    "bot-stats": bot_stats,
    "profile-picture": profile_picture,
    "banner": banner,
    "cat-pic": cat_pic,
    "member-count": member_count,
    # HELP CMDS
    "help category": help_category,
    "help command": help_command,
    # MATH CMDS
    "math add": math_add,
    "math sum": math_sum,
    "math sub": math_sub,
    "math mul": math_mul,
    "math prod": math_prod,
    "math div": math_div,
    "math floordiv": math_floordiv,
    "math pow": math_pow,
    "math mod": math_mod,
    "math sqrt": math_sqrt,
    "math cbrt": math_cbrt,
    "math nroot": math_nroot,
    "math abs": math_abs,
    "math ceil": math_ceil,
    "math floor": math_floor,
    "math round": math_round,
    "math log": math_log,
    "math ln": math_ln,
    "math gcd": math_gcd,
    "math gcd-bulk": math_gcd_bulk,
    "math lcm": math_lcm,
    "math lcm-bulk": math_lcm_bulk,
    "math distance cartesian-2d": math_distance_cartesian_2d,
    "math distance cartesian-3d": math_distance_cartesian_3d,
    "math factorial": math_factorial,
    # RANDOM CMDS
    "random integer": random_integer,
    "random decimal": random_decimal,
    "random choice": random_choice,
    "random shuffle": random_shuffle,
    # STATS CMDS
    "stats mean": stats_mean,
    "stats median": stats_median,
    "stats mode": stats_mode,
    "stats multimode": stats_multimode,
}

PRIVATE = MANAGEMENT + MODERATION
PRIVATE_COMMAND_MAP = {
    # MANAGEMENT CMDS
    "mgmt echo": mgmt_echo,
    "mgmt dm": mgmt_dm,
    "mgmt announce": mgmt_announce,
    # MODERATION CMDS
    "mod ban": mod_ban,
    "mod unban": mod_unban,
    "mod timeout add": mod_timeout_add,
    "mod timeout reduce": mod_timeout_reduce,
    "mod timeout remove": mod_timeout_remove,
    "mod clear": mod_clear,
    "mod warn": mod_warn,
    "mod kick": mod_kick,
    "mod mute": mod_mute,
    "mod unmute": mod_unmute,
}
