"""
commands.py
Contains definitions of commands to be used with the /help command.
"""

from typing import Literal, Union

from discord import Member, Role, TextChannel, User

from .representations import Command, Param

HelpCategory = Literal["color roles", "color tools", "help", "math"]
ClassifiedHelpCategory = Literal["management", "moderation"]

# # # # # # #
# HELP CMDS #
# # # # # # #

help_category = Command(
    name="category",
    description="List information about all the commands in a category",
    group="help",
)
help_category.add_param(
    Param(
        name="category",
        type=HelpCategory,
        description="Command category to get help for",
    )
)

help_command = Command(
    name="command", description="Get help for a specific command.", group="help"
)
help_command.add_param(
    Param(name="cmd", type=str, description="Command to get help for")
)

# # # # # # # # # #
# COLOR ROLE CMDS #
# # # # # # # # # #

role_assign_hex = Command(
    name="hex",
    description="Assign yourself a custom color role with a hex value.",
    group="color-role",
)
role_assign_hex.add_param(
    Param(name="hex", type=str, description="Hex value (#000000-#ffffff)")
)

role_assign_rgb = Command(
    name="rgb",
    description="Assign yourself a custom color role with an RGB value.",
    group="color-role",
)
role_assign_rgb.add_param(Param(name="r", type=int, description="Red value (0-255)"))
role_assign_rgb.add_param(Param(name="g", type=int, description="Green value (0-255)"))
role_assign_rgb.add_param(Param(name="b", type=int, description="Blue value (0-255)"))

role_assign_name = Command(
    name="name",
    description="Assign yourself a custom color role with a color name.",
    group="color-role",
)
role_assign_name.add_param(
    Param(
        name="name",
        type=str,
        description="Color name (use /colors for a list of allowed colors)",
    )
)

role_assign_random = Command(
    name="random",
    description="Assign yourself a custom color role with a randomly generated color.",
    group="color-role",
)
role_assign_random.add_param(
    Param(
        name="seed",
        type=Union[str, None],
        description="Optional seed to use when generating the random color",
        optional=True,
    )
)

role_assign_copy = Command(
    name="copy-color",
    description="Assign yourself a custom color role by copying another role's color.",
    group="color-role",
)
role_assign_copy.add_param(
    Param(name="role", type=Role, description="Role to copy the color of")
)

role_assign_reset = Command(
    name="reset",
    description="Reset your color role's color to the default Discord color (invisible, #000000).",
    group="color-role",
)

role_assign_reassign = Command(
    name="reassign",
    description="Check if you are missing your color role, "
    + "and reassign it if so and the role exists.",
    group="color-role",
)

# # # # # # # # # #
# COLOR TOOL CMDS #
# # # # # # # # # #

colors = Command(
    name="colors",
    description="Provides a list of all allowed color names used with CatBot.",
)
colors.add_param(
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
    name="rgb",
    description="Get information about an RGB color, "
    + "such as its hex equivalent and its color name equivalent, "
    + "if available, and an image preview.",
    group="color-info",
)
color_info_rgb.add_param(Param(name="r", type=int, description="Red value (0-255)"))
color_info_rgb.add_param(Param(name="g", type=int, description="Green value (0-255)"))
color_info_rgb.add_param(Param(name="b", type=int, description="Blue value (0-255)"))

color_info_hex = Command(
    name="hex",
    description="Get information about a hex color, "
    + "such as its RGB equivalent and its color name equivalent, "
    + "if available, and an image preview.",
    group="color-info",
)
color_info_hex.add_param(
    Param(name="hex", type=str, description="Hex value (#000000-#ffffff)")
)

color_info_name = Command(
    name="name",
    description="Get information about a color name, "
    + "such as its hex and RGB equivalents and its color name equivalent, "
    + "if available, and an image preview.",
    group="color-info",
)
color_info_name.add_param(
    Param(
        name="name",
        type=str,
        description="Color name (use /colors for a list of allowed colors)",
    )
)

color_info_role = Command(
    name="role",
    description="Get information about a role's color, "
    + "such as its hex and RGB equivalents and its color name equivalent, "
    + "if available, and an image preview.",
    group="color-info",
)
color_info_role.add_param(
    Param(name="role", type=Role, description="Role to get the color information of")
)

random_color = Command(name="random-color", description="Generate a random color.")
random_color.add_param(
    Param(
        name="seed",
        type=Union[str, None],
        description="Optional seed to use when generating the random color",
        optional=True,
    )
)

invert_rgb = Command(
    name="rgb", description="Invert an RGB color.", group="invert-color"
)
invert_rgb.add_param(Param(name="r", type=int, description="Red value (0-255)"))
invert_rgb.add_param(Param(name="g", type=int, description="Green value (0-255)"))
invert_rgb.add_param(Param(name="b", type=int, description="Blue value (0-255)"))

invert_hex = Command(
    name="hex", description="Invert a hex color.", group="invert-color"
)
invert_hex.add_param(
    Param(name="hex", type=str, description="Hex value (#000000-#ffffff)")
)

invert_name = Command(
    name="name", description="Invert a color name.", group="invert-color"
)
invert_name.add_param(
    Param(
        name="name",
        type=str,
        description="Color name (use /colors for a list of allowed colors)",
    )
)

# # # # # # # # # #
# MANAGEMENT CMDS #
# # # # # # # # # #

echo = Command(name="echo", description="Echo a message back to a channel.")
echo.add_param(Param(name="message", type=str, description="Message to echo"))
echo.add_param(
    Param(
        name="channel",
        type=Union[TextChannel, None],
        description="Channel to send the echoed message to; defaults to current channel if empty",
    )
)

dm = Command(name="dm", description="Send a direct message to a user.")
dm.add_param(
    Param(name="user", type=User, description="User to send the direct message to")
)
dm.add_param(Param(name="message", type=str, description="Message to send to the user"))

announce = Command(name="announce", description="Announce a message to a channel.")
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

# # # # # # # # # #
# MODERATION CMDS #
# # # # # # # # # #

ban = Command(name="ban", description="Ban a user.")
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

unban = Command(name="unban", description="Unban a user.")
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
    name="add", description="Add time to a user's timeout.", group="timeout"
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
    name="reduce", description="Reduce time from a user's timeout.", group="timeout"
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
    name="remove", description="Remove a user's timeout.", group="timeout"
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

clear = Command(name="clear", description="Delete a number of messages from a channel.")
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

warn = Command(name="warn", description="Warn a user.")
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

kick = Command(name="kick", description="Kick a user.")
kick.add_param(Param(name="user", type=Member, description="User to kick"))
kick.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Kick reason",
        optional=True,
    )
)

mute = Command(name="mute", description="Mute a user.")
mute.add_param(Param(name="user", type=Member, description="User to mute"))
mute.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Mute reason",
        optional=True,
    )
)

unmute = Command(name="unmute", description="Unmute a user.")
unmute.add_param(Param(name="user", type=Member, description="User to unmute"))
unmute.add_param(
    Param(
        name="reason",
        type=Union[str, None],
        description="Unmute reason",
        optional=True,
    )
)

# # # # # # #
# MATH CMDS #
# # # # # # #

add = Command(name="add", description="Add two numbers.")
add.add_param(Param(name="x", type=float, description="First number"))
add.add_param(Param(name="y", type=float, description="Second number"))

sum_ = Command(
    name="sum", description="Calculate the sum of an arbitrary amount of numbers."
)
sum_.add_param(
    Param(name="numbers", type=str, description="Numbers to sum, separated by commas")
)

sub = Command(name="sub", description="Subtract two numbers.")
sub.add_param(Param(name="x", type=float, description="First number"))
sub.add_param(Param(name="y", type=float, description="Second number"))

mul = Command(name="mul", description="Multiply two numbers.")
mul.add_param(Param(name="x", type=float, description="First number"))
mul.add_param(Param(name="y", type=float, description="Second number"))

prod = Command(
    name="prod",
    description="Calculate the product of an arbitrary amount of numbers.",
)
prod.add_param(
    Param(
        name="numbers",
        type=str,
        description="Numbers to find the product of, separated by commas",
    )
)

div = Command(name="div", description="Divide two numbers.")
div.add_param(Param(name="x", type=float, description="First number"))
div.add_param(Param(name="y", type=float, description="Second number"))

floordiv = Command(name="floordiv", description="Divide two numbers and floor it.")
floordiv.add_param(Param(name="x", type=float, description="First number"))
floordiv.add_param(Param(name="y", type=float, description="Second number"))

pow_ = Command(name="pow", description="Raise a number to the power of another.")
pow_.add_param(Param(name="x", type=float, description="First number"))
pow_.add_param(Param(name="y", type=float, description="Second number"))

mod = Command(name="mod", description="Calculate the modulus of two numbers.")
mod.add_param(Param(name="x", type=float, description="First number"))
mod.add_param(Param(name="y", type=float, description="Second number"))

sqrt = Command(name="sqrt", description="Calculate the square root of a number.")
sqrt.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the square root of",
    )
)

cbrt = Command(name="cbrt", description="Calculate the cube root of a number.")
cbrt.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the cube root of",
    )
)

nroot = Command(name="nroot", description="Calculate the nth root of a number.")
nroot.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the nth root of",
    )
)

abs_ = Command(name="abs", description="Calculate the absolute value of a number.")
abs_.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the absolute value of",
    )
)

ceil = Command(name="ceil", description="Calculate the ceiling of a number.")
ceil.add_param(
    Param(
        name="x",
        type=float,
        description="Number to calculate the ceiling of",
    )
)

floor = Command(name="floor", description="Calculate the floor of a number.")
floor.add_param(
    Param(name="x", type=float, description="Number to calculate the floor of")
)

round_ = Command(
    name="round", description="Round a number to a specified number of digits."
)
round_.add_param(Param(name="x", type=float, description="Number to round"))
round_.add_param(
    Param(name="ndigits", type=int, description="Number of digits to round to")
)

log = Command(name="log", description="Calculate the logarithm of a number.")
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
    name="gcd",
    description="Calculate the greatest common divisor/denominator (GDC) of two numbers",
)
gcd.add_param(Param(name="x", type=int, description="First number"))
gcd.add_param(Param(name="y", type=int, description="Second number"))

gcd_bulk = Command(
    name="gcd-bulk", description="Calculate the GCD of an arbitrary amount of numbers."
)
gcd_bulk.add_param(
    Param(
        name="numbers",
        type=str,
        description="Numbers to find the GCD of, separated by commas",
    )
)

lcm = Command(
    name="lcm",
    description="Calculate the least common multiplier (LCM) of two numbers.",
)
lcm.add_param(Param(name="x", type=int, description="First number"))
lcm.add_param(Param(name="y", type=int, description="Second number"))

lcm_bulk = Command(
    name="lcm-bulk",
    description="Calculate the LCM of an arbitrary amount of numbers.",
)
lcm_bulk.add_param(
    Param(
        name="numbers",
        type=str,
        description="Numbers to find the LCM of, separated by commas",
    )
)

distance_cartesian_2d = Command(
    name="cartesian-2d",
    description="Calculate the Cartesian distance between two points in 2D space.",
    group="distance",
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
    name="cartesian-3d",
    description="Calculate the Cartesian distance between two points in 3D space.",
    group="distance",
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
    name="factorial", description="Calculate the factorial of a number."
)
factorial.add_param(
    Param(name="x", type=int, description="Number to calculate the factorial of")
)

# # # # # # # # #
# CMD LIST INIT #
# # # # # # # # #

HELP = (help_category, help_command)
COLOR_ROLES = (
    role_assign_hex,
    role_assign_rgb,
    role_assign_name,
    role_assign_random,
    role_assign_copy,
    role_assign_reset,
    role_assign_reassign,
)
COLOR_TOOLS = (
    colors,
    color_info_rgb,
    color_info_hex,
    color_info_name,
    color_info_role,
    random_color,
    invert_rgb,
    invert_hex,
    invert_name,
)
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

PUBLIC = HELP + COLOR_ROLES + COLOR_TOOLS + MATH
PUBLIC_COMMAND_MAP = {
    "help-category": help_category,
    "help-command": help_command,
    "color-role hex": role_assign_hex,
    "color-role rgb": role_assign_rgb,
    "color-role name": role_assign_name,
    "color-role random": role_assign_random,
    "color-role copy": role_assign_copy,
    "color-role reset": role_assign_reset,
    "color-role reassign": role_assign_reassign,
    "colors": colors,
    "color-info rgb": color_info_rgb,
    "color-info hex": color_info_hex,
    "color-info name": color_info_name,
    "color-info role": color_info_role,
    "random-color": random_color,
    "invert-color rgb": invert_rgb,
    "invert-color hex": invert_hex,
    "invert-color name": invert_name,
    "add": add,
    "sum": sum_,
    "sub": sub,
    "mul": mul,
    "prod": prod,
    "div": div,
    "floordiv": floordiv,
    "pow": pow_,
    "mod": mod,
    "sqrt": sqrt,
    "cbrt": cbrt,
    "nroot": nroot,
    "abs": abs_,
    "ceil": ceil,
    "floor": floor,
    "round": round_,
    "log": log,
    "gcd": gcd,
    "gcd-bulk": gcd_bulk,
    "lcm": lcm,
    "lcm-bulk": lcm_bulk,
    "distance cartesian-2d": distance_cartesian_2d,
    "distance cartesian-3d": distance_cartesian_3d,
    "factorial": factorial,
}

PRIVATE = MANAGEMENT + MODERATION
PRIVATE_COMMAND_MAP = {
    "ban": ban,
    "timeout-add": timeout_add,
    "timeout-reduce": timeout_reduce,
    "timeout-remove": timeout_remove,
    "clear": clear,
    "warn": warn,
    "kick": kick,
    "mute": mute,
    "unmute": unmute,
    "echo": echo,
    "dm": dm,
    "announce": announce,
}
