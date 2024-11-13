"""
commands.py
Contains definitions of commands to be used with the /help command.
"""

from typing import Literal, Union

from discord import Role, User

from .representations import Command, Param

HelpCategory = Literal["color roles", "color tools", "help"]
ClassifiedHelpCategory = Literal["moderation"]

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
        default=None,
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
        default=None,
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
        default=None,
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

MODERATION = (ban,)

PUBLIC = HELP + COLOR_ROLES + COLOR_TOOLS
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
}

PRIVATE = MODERATION
PRIVATE_COMMAND_MAP = {"ban": ban}
