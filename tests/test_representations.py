# pylint: disable=all

import pytest
from discord import TextChannel, User
from CatBot.help.representations import (
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
        == "Repeat the phrase given into the output channel\n**Parameters:**\n**channel** - Channel to output the phrase to\n(*TextChannel*)"
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
        == "Exponentiate a number to another\n**Parameters:**\n**x** - Base\n(*integer*)\n**y** - Exponent\n(*integer*)\n**modulo** - Modulus to apply after exponentiation\n(*integer*, defaults to *1*)"
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
        == "Set a status\n**Parameters:**\n**status** - The status to change to\n(Specific Value(s): *'active'* or *'idle'* or *'do not disturb'* or *'offline'*)"
    )


def test_mixed():
    cmd = Command(name="fun ping", description="Ping someone!")
    cmd.add_param(Param(name="user", type=User, description="The user to ping"))
    cmd.add_param(
        Param(
            name="message",
            type=str,
            description="Optional message to attach",
            optional=True,
        )
    )

    assert generate_field_title(cmd) == "/fun ping"
    assert (
        generate_field_description(cmd)
        == "Ping someone!\n**Parameters:**\n**user** - The user to ping\n(*User*)\n**message** - Optional message to attach\n(*text*, optional)"
    )


if __name__ == "__main__":
    pytest.main()
