"""
commands.py
Contains definitions of commands to be used with the /help command.
"""

# pylint: disable=too-many-lines

from typing import Literal, Union

from discord import Member, Role, TextChannel, User

from .representations import Command, Param

HelpCategory = Literal["color", "date-time", "fun", "help", "math", "random"]
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

color_role_copy = Command(
    name="color role copy-color",
    description="Assign yourself a custom color role by copying another role's color.",
)
color_role_copy.add_param(
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

color_list = Command(
    name="color color-list",
    description="Provides a list of all allowed color names used with CatBot.",
)
color_list.add_param(
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

datetime_datetime = Command(
    name="date-time date-time", description="Get the date and time in a timezone"
)
datetime_datetime.add_param(
    Param(
        name="timezone",
        type=str,
        description="The timezone to get the date and time in",
    )
)
datetime_datetime.add_param(
    Param(
        name="military_time",
        type=bool,
        description="Whether to use military (24-hour) time",
        optional=True,
        default=False,
    )
)
datetime_datetime.add_param(
    Param(
        name="seconds",
        type=bool,
        description="Whether to include seconds in the time",
        optional=True,
        default=False,
    )
)
datetime_datetime.add_param(
    Param(
        name="microseconds",
        type=bool,
        description="Whether to include microseconds in the time "
        + "(if True, seconds are included too)",
        optional=True,
        default=False,
    )
)

datetime_date = Command(name="date-time date", description="Get the date in a timezone")
datetime_date.add_param(
    Param(name="timezone", type=str, description="The timezone to get the date in")
)

datetime_time = Command(name="date-time time", description="Get the time in a timezone")
datetime_time.add_param(
    Param(name="timezone", type=str, description="The timezone to get the time in")
)
datetime_time.add_param(
    Param(
        name="military_time",
        type=bool,
        description="Whether to use military (24-hour) time",
        optional=True,
        default=False,
    )
)
datetime_time.add_param(
    Param(
        name="seconds",
        type=bool,
        description="Whether to include seconds in the time",
        optional=True,
        default=False,
    )
)
datetime_time.add_param(
    Param(
        name="microseconds",
        type=bool,
        description="Whether to include microseconds in the time "
        + "(if True, seconds are included too)",
        optional=True,
        default=False,
    )
)

# # # # # # # # #
# FUN/MISC CMDS #
# # # # # # # # #

flip_coin = Command(name="flip-coin", description="Flip a coin")

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

echo = Command(name="mgmt echo", description="Echo a message back to a channel.")
echo.add_param(Param(name="message", type=str, description="Message to echo"))
echo.add_param(
    Param(
        name="channel",
        type=Union[TextChannel, None],
        description="Channel to send the echoed message to; defaults to current channel if empty",
    )
)

dm = Command(name="mgmt dm", description="Send a direct message to a user.")
dm.add_param(
    Param(name="user", type=User, description="User to send the direct message to")
)
dm.add_param(Param(name="message", type=str, description="Message to send to the user"))

announce = Command(name="mgmt announce", description="Announce a message to a channel.")
announce.add_param(Param(name="message", type=str, description="Message to announce"))
announce.add_param(
    Param(
        name="channel",
        type=Union[TextChannel, None],
        description="Channel to send the announced message to; "
        + "defaults to current channel if empty",
    )
)
announce.add_param(
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

add = Command(name="math add", description="Add two numbers.")
add.add_param(Param(name="x", type=float, description="First number"))
add.add_param(Param(name="y", type=float, description="Second number"))

sum_ = Command(
    name="math sum", description="Calculate the sum of an arbitrary amount of numbers."
)
sum_.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to sum, separated by commas (e.g. "1,2,3")',
    )
)

sub = Command(name="math sub", description="Subtract two numbers.")
sub.add_param(Param(name="x", type=float, description="First number"))
sub.add_param(Param(name="y", type=float, description="Second number"))

mul = Command(name="math mul", description="Multiply two numbers.")
mul.add_param(Param(name="x", type=float, description="First number"))
mul.add_param(Param(name="y", type=float, description="Second number"))

prod = Command(
    name="math prod",
    description="Calculate the product of an arbitrary amount of numbers.",
)
prod.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to find the product of, separated by commas (e.g. "1,2,3")',
    )
)

div = Command(name="math div", description="Divide two numbers.")
div.add_param(Param(name="x", type=float, description="First number"))
div.add_param(Param(name="y", type=float, description="Second number"))

floordiv = Command(name="math floordiv", description="Divide two numbers and floor it.")
floordiv.add_param(Param(name="x", type=float, description="First number"))
floordiv.add_param(Param(name="y", type=float, description="Second number"))

pow_ = Command(name="math pow", description="Raise a number to the power of another.")
pow_.add_param(Param(name="x", type=float, description="First number"))
pow_.add_param(Param(name="y", type=float, description="Second number"))

mod = Command(name="math mod", description="Calculate the modulus of two numbers.")
mod.add_param(Param(name="x", type=float, description="First number"))
mod.add_param(Param(name="y", type=float, description="Second number"))

sqrt = Command(name="math sqrt", description="Calculate the square root of a number.")
sqrt.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the square root of",
    )
)

cbrt = Command(name="math cbrt", description="Calculate the cube root of a number.")
cbrt.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the cube root of",
    )
)

nroot = Command(name="math nroot", description="Calculate the nth root of a number.")
nroot.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the nth root of",
    )
)

abs_ = Command(name="math abs", description="Calculate the absolute value of a number.")
abs_.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the absolute value of",
    )
)

ceil = Command(name="math ceil", description="Calculate the ceiling of a number.")
ceil.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the ceiling of",
    )
)

floor = Command(name="math floor", description="Calculate the floor of a number.")
floor.add_param(
    Param(name="x", type=float, description="Number to calculate the floor of")
)

round_ = Command(
    name="math round", description="Round a number to a specified number of digits."
)
round_.add_param(Param(name="x", type=float, description="Number to round"))
round_.add_param(
    Param(name="ndigits", type=int, description="Number of digits to round to")
)

log = Command(name="math log", description="Calculate the logarithm of a number.")
log.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the logarithm of",
    )
)
log.add_param(
    Param(
        name="base",
        type=Union[float, None],
        description="Base of the logarithm; if left empty, uses base e",
    )
)

gcd = Command(
    name="math gcd",
    description="Calculate the greatest common divisor/denominator (GDC) of two numbers",
)
gcd.add_param(Param(name="x", type=int, description="First number"))
gcd.add_param(Param(name="y", type=int, description="Second number"))

gcd_bulk = Command(
    name="math gcd-bulk",
    description="Calculate the GCD of an arbitrary amount of numbers.",
)
gcd_bulk.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to find the GCD of, separated by commas (e.g. "1,2,3")',
    )
)

lcm = Command(
    name="math lcm",
    description="Calculate the least common multiplier (LCM) of two numbers.",
)
lcm.add_param(Param(name="x", type=int, description="First number"))
lcm.add_param(Param(name="y", type=int, description="Second number"))

lcm_bulk = Command(
    name="math lcm-bulk",
    description="Calculate the LCM of an arbitrary amount of numbers.",
)
lcm_bulk.add_param(
    Param(
        name="numbers",
        type=str,
        description='Numbers to find the LCM of, separated by commas (e.g. "1,2,3")',
    )
)

distance_cartesian_2d = Command(
    name="math distance cartesian-2d",
    description="Calculate the Cartesian distance between two points in 2D space.",
)
distance_cartesian_2d.add_param(
    Param(name="x1", type=float, description="First x-coordinate")
)
distance_cartesian_2d.add_param(
    Param(name="y1", type=float, description="First y-coordinate")
)
distance_cartesian_2d.add_param(
    Param(name="x2", type=float, description="Second x-coordinate")
)
distance_cartesian_2d.add_param(
    Param(name="y2", type=float, description="Second y-coordinate")
)

distance_cartesian_3d = Command(
    name="math distance cartesian-3d",
    description="Calculate the Cartesian distance between two points in 3D space.",
)
distance_cartesian_3d.add_param(
    Param(name="x1", type=float, description="First x-coordinate")
)
distance_cartesian_3d.add_param(
    Param(name="y1", type=float, description="First y-coordinate")
)
distance_cartesian_3d.add_param(
    Param(name="z1", type=float, description="First z-coordinate")
)
distance_cartesian_3d.add_param(
    Param(name="x2", type=float, description="Second x-coordinate")
)
distance_cartesian_3d.add_param(
    Param(name="y2", type=float, description="Second y-coordinate")
)
distance_cartesian_3d.add_param(
    Param(name="z2", type=float, description="Second z-coordinate")
)

factorial = Command(
    name="math factorial", description="Calculate the factorial of a number."
)
factorial.add_param(
    Param(name="x", type=int, description="Number to calculate the factorial of")
)

# # # # # # # # # #
# MODERATION CMDS #
# # # # # # # # # #

ban = Command(name="mod ban", description="Ban a user.")
ban.add_param(Param(name="user", type=User, description="User to ban"))
ban.add_param(
    Param(
        name="delete_message_time",
        type=int,
        description="How much of the user's message history to delete",
        optional=True,
        default=0,
    )
)
ban.add_param(
    Param(
        name="time_unit",
        type=Literal["seconds", "minutes", "hours", "days"],
        description="Unit of time",
        optional=True,
        default="seconds",
    )
)
ban.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Ban reason",
        optional=True,
    )
)
ban.add_param(
    Param(
        name="ghost",
        type=bool,
        description="Don't notify the user",
        optional=True,
        default=False,
    )
)

unban = Command(name="mod unban", description="Unban a user.")
unban.add_param(Param(name="user_id", type=str, description="ID of the user to unban"))
unban.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Unban reason",
        optional=True,
    )
)

timeout_add = Command(
    name="mod timeout add", description="Add time to a user's timeout."
)
timeout_add.add_param(
    Param(name="user", type=Member, description="User to add timeout time to")
)
timeout_add.add_param(Param(name="time", type=int, description="Timeout addition time"))
timeout_add.add_param(
    Param(
        name="time_unit",
        type=Literal["seconds", "minutes", "hours", "days"],
        description="Unit of time",
        optional=True,
        default="seconds",
    )
)
timeout_add.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Timeout addition reason",
        optional=True,
    )
)

timeout_reduce = Command(
    name="mod timeout reduce", description="Reduce time from a user's timeout."
)
timeout_reduce.add_param(
    Param(name="user", type=Member, description="User to reduce timeout time from")
)
timeout_reduce.add_param(
    Param(name="time", type=int, description="Timeout reduction time")
)
timeout_reduce.add_param(
    Param(
        name="time_unit",
        type=Literal["seconds", "minutes", "hours", "days"],
        description="Unit of time",
        optional=True,
        default="seconds",
    )
)
timeout_reduce.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Timeout reduction reason",
        optional=True,
    )
)

timeout_remove = Command(
    name="mod timeout remove", description="Remove a user's timeout."
)
timeout_remove.add_param(
    Param(name="user", type=Member, description="User to remove timeout from")
)
timeout_remove.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Timeout removal reason",
        optional=True,
    )
)

clear = Command(
    name="mod clear", description="Delete a number of messages from a channel."
)
clear.add_param(
    Param(name="amount", type=int, description="Number of messages to delete")
)
clear.add_param(
    Param(
        name="channel",
        type=Union[TextChannel, None],
        description="Channel to delete messages from; defaults to current channel if empty",
        optional=True,
    )
)
clear.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Deletion reason",
        optional=True,
    )
)

warn = Command(name="mod warn", description="Warn a user.")
warn.add_param(Param(name="user", type=Member, description="User to warn"))
warn.add_param(
    Param(
        name="channel", type=TextChannel, description="Channel to send the warning in"
    )
)
warn.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Warning reason",
        optional=True,
    )
)

kick = Command(name="mod kick", description="Kick a user.")
kick.add_param(Param(name="user", type=Member, description="User to kick"))
kick.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Kick reason",
        optional=True,
    )
)

mute = Command(name="mod mute", description="Mute a user.")
mute.add_param(Param(name="user", type=Member, description="User to mute"))
mute.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Mute reason",
        optional=True,
    )
)

unmute = Command(name="mod unmute", description="Unmute a user.")
unmute.add_param(Param(name="user", type=Member, description="User to unmute"))
unmute.add_param(
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
        optional=True,
        default=0,
    )
)
random_integer.add_param(
    Param(
        name="b",
        type=int,
        description="The right endpoint (inclusive)",
        optional=True,
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
        optional=True,
        default=0.0,
    )
)
random_decimal.add_param(
    Param(
        name="b",
        type=float,
        description="The right endpoint (inclusive)",
        optional=True,
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
        optional=True,
        default=1,
    )
)
random_choice.add_param(
    Param(
        name="duplicates",
        type=bool,
        description="Whether the same choice can be made multiple times",
        optional=True,
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
        description='A list of values separated by commas (e.g. "1,2,3,a,b,c")',
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

# # # # # # #
# STATS CMD #
# # # # # # #

stats = Command(name="stats", description="Get statistics about CatBot.")

# # # # # # # # #
# CMD LIST INIT #
# # # # # # # # #

COLOR = (
    color_role_hex,
    color_role_rgb,
    color_role_name,
    color_role_random,
    color_role_copy,
    color_role_reset,
    color_role_reassign,
    color_list,
    color_info_rgb,
    color_info_hex,
    color_info_name,
    color_info_role,
    color_random,
    color_invert_rgb,
    color_invert_hex,
    color_invert_name,
)
DATETIME = (datetime_datetime, datetime_date, datetime_time)
FUN = (flip_coin, stats)
HELP = (help_category, help_command)
MATH = (
    add,
    sum_,
    sub,
    mul,
    prod,
    div,
    floordiv,
    pow_,
    mod,
    sqrt,
    cbrt,
    nroot,
    abs_,
    ceil,
    floor,
    round_,
    log,
    gcd,
    gcd_bulk,
    lcm,
    lcm_bulk,
    distance_cartesian_2d,
    distance_cartesian_3d,
    factorial,
)
RANDOM = (random_integer, random_decimal, random_choice, random_shuffle)

MANAGEMENT = (echo, dm, announce)
MODERATION = (
    ban,
    timeout_add,
    timeout_reduce,
    timeout_remove,
    clear,
    warn,
    kick,
    mute,
    unmute,
)


PUBLIC = COLOR + DATETIME + FUN + HELP + MATH + RANDOM
PUBLIC_COMMAND_MAP = {
    # COLOR CMDS
    "color role hex": color_role_hex,
    "color role rgb": color_role_rgb,
    "color role name": color_role_name,
    "color role random": color_role_random,
    "color role copy": color_role_copy,
    "color role reset": color_role_reset,
    "color role reassign": color_role_reassign,
    "color color-list": color_list,
    "color info rgb": color_info_rgb,
    "color info hex": color_info_hex,
    "color info name": color_info_name,
    "color info role": color_info_role,
    "color random": color_random,
    "color invert rgb": color_invert_rgb,
    "color invert hex": color_invert_hex,
    "color invert name": color_invert_name,
    # DATETIME CMDS
    "date-time date-time": datetime_datetime,
    "date-time date": datetime_date,
    "date-time time": datetime_time,
    # FUN CMDS
    "flip-coin": flip_coin,
    "stats": stats,
    # HELP CMDS
    "help category": help_category,
    "help command": help_command,
    # MATH CMDS
    "math add": add,
    "math sum": sum_,
    "math sub": sub,
    "math mul": mul,
    "math prod": prod,
    "math div": div,
    "math floordiv": floordiv,
    "math pow": pow_,
    "math mod": mod,
    "math sqrt": sqrt,
    "math cbrt": cbrt,
    "math nroot": nroot,
    "math abs": abs_,
    "math ceil": ceil,
    "math floor": floor,
    "math round": round_,
    "math log": log,
    "math gcd": gcd,
    "math gcd-bulk": gcd_bulk,
    "math lcm": lcm,
    "math lcm-bulk": lcm_bulk,
    "math distance cartesian-2d": distance_cartesian_2d,
    "math distance cartesian-3d": distance_cartesian_3d,
    "math factorial": factorial,
    # RANDOM CMDS
    "random integer": random_integer,
    "random decimal": random_decimal,
    "random choice": random_choice,
    "random shuffle": random_shuffle,
}

PRIVATE = MANAGEMENT + MODERATION
PRIVATE_COMMAND_MAP = {
    # MANAGEMENT CMDS
    "mgmt echo": echo,
    "mgmt dm": dm,
    "mgmt announce": announce,
    # MODERATION CMDS
    "mod ban": ban,
    "mod unban": unban,
    "mod timeout add": timeout_add,
    "mod timeout reduce": timeout_reduce,
    "mod timeout remove": timeout_remove,
    "mod clear": clear,
    "mod warn": warn,
    "mod kick": kick,
    "mod mute": mute,
    "mod unmute": unmute,
}
