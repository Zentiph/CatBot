# pylint: disable=all

import pytest
from discord import TextChannel, User
from CatBot.representations import (
    Param,
    Command,
    generate_field_description,
    generate_field_title,
)
from typing import Literal, Union


def test_base():
    cmd = Command(name="echo", description="Repeat the phrase given")

    assert generate_field_title(cmd) == "/echo"
    assert generate_field_description(cmd) == "Repeat the phrase given"


def test_params():
    cmd = Command(
        name="echo", description="Repeat the phrase given into the output channel"
    )
    cmd.add_param(
        Param(
            name="channel",
            type=TextChannel,
            description="Channel to output the phrase to",
        )
    )

    assert generate_field_title(cmd) == "/echo"
    assert (
        generate_field_description(cmd)
        == "Repeat the phrase given into the output channel\nParameters:\nchannel - Channel to output the phrase to\n(TextChannel)"
    )


def test_group():
    cmd = Command(name="add", description="Add two numbers", group="math")
    cmd.add_param(Param(name="x", type=int, description="First number"))
    cmd.add_param(Param(name="y", type=int, description="Second number"))

    assert generate_field_title(cmd) == "/math add"
    assert (
        generate_field_description(cmd)
        == "Add two numbers\nParameters:\nx - First number\n(int)\ny - Second number\n(int)"
    )


def test_default():
    cmd = Command(name="pow", description="Exponentiate a number to another")
    cmd.add_param(Param(name="x", type=int, description="Base"))
    cmd.add_param(Param(name="y", type=int, description="Exponent"))
    cmd.add_param(
        Param(
            name="modulo",
            type=int,
            description="Modulus to apply after exponentiation",
            default=1,
        )
    )

    assert generate_field_title(cmd) == "/pow"
    assert (
        generate_field_description(cmd)
        == "Exponentiate a number to another\nParameters:\nx - Base\n(int)\ny - Exponent\n(int)\nmodulo - Modulus to apply after exponentiation\n(int, defaults to 1)"
    )


def test_union():
    cmd = Command(name="add", description="Add two numbers", group="math")
    cmd.add_param(Param(name="x", type=Union[int, float], description="First number"))
    cmd.add_param(Param(name="y", type=Union[int, float], description="Second number"))

    assert generate_field_title(cmd) == "/math add"
    assert (
        generate_field_description(cmd)
        == "Add two numbers\nParameters:\nx - First number\n(int or float)\ny - Second number\n(int or float)"
    )


def test_literal():
    cmd = Command(name="set-status", description="Set a status")
    cmd.add_param(
        Param(
            name="status",
            type=Literal["active", "idle", "do not disturb", "offline"],
            description="The status to change to",
        )
    )

    assert generate_field_title(cmd) == "/set-status"
    assert (
        generate_field_description(cmd)
        == "Set a status\nParameters:\nstatus - The status to change to\n(Specific Value(s): 'active' or 'idle' or 'do not disturb' or 'offline')"
    )


def test_mixed():
    cmd = Command(name="ping", description="Ping someone!", group="fun")
    cmd.add_param(Param(name="user", type=User, description="The user to ping"))
    cmd.add_param(
        Param(
            name="message",
            type=Union[str, None],
            description="Optional message to attach",
            optional=True,
            default=None,
        )
    )

    assert generate_field_title(cmd) == "/fun ping"
    assert (
        generate_field_description(cmd)
        == "Ping someone!\nParameters:\nuser - The user to ping\n(User)\nmessage - Optional message to attach\n(str or NoneType, optional, defaults to None)"
    )


if __name__ == "__main__":
    pytest.main()
