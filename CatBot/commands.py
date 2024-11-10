"""
commands.py
Contains definitions of commands to be used with the /help command.
"""

from typing import Literal, Union

from discord import Role

from .representations import Command, Param

role_assign_hex = Command(
    name="hex",
    description="Assign yourself a custom color role with a hex value.",
    group="role-assign",
)
role_assign_hex.add_param(
    Param(name="hex", type=str, description="Hex value (#000000-#ffffff)")
)

role_assign_rgb = Command(
    name="rgb",
    description="Assign yourself a custom color role with an RGB value.",
    group="role-assign",
)
role_assign_rgb.add_param(Param(name="r", type=int, description="Red value (0-255)"))
role_assign_rgb.add_param(Param(name="g", type=int, description="Green value (0-255)"))
role_assign_rgb.add_param(Param(name="b", type=int, description="Blue value (0-255)"))

role_assign_name = Command(
    name="name",
    description="Assign yourself a custom color role with a color name.",
    group="role-assign",
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
    group="role-assign",
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
    group="role-assign",
)
role_assign_copy.add_param(
    Param(name="role", type=Role, description="Role to copy the color of")
)

role_assign_reset = Command(
    name="reset",
    description="Reset your color role's color to the default Discord color (invisible, #000000).",
    group="role-assign",
)

role_assign_reassign = Command(
    name="reassign",
    description="Check if you are missing your color role, "
    + "and reassign it if so and the role exists.",
    group="role-assign",
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

ALL = COLOR_ROLES + COLOR_TOOLS
COMMAND_MAP = {
    "role-assign hex": role_assign_hex,
    "role-assign rgb": role_assign_rgb,
    "role-assign name": role_assign_name,
    "role-assign random": role_assign_random,
    "role-assign copy": role_assign_copy,
    "role-assign reset": role_assign_reset,
    "role-assign reassign": role_assign_reassign,
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
