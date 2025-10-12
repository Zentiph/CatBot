"""
A confirmation embed that provides the user
with confirmation and cancellation options for
confirmation-based interactions.
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

import discord
from discord import ui

__author__ = "Gavin Borne"
__license__ = "MIT"

AsyncFunction = Callable[..., Awaitable[Any]]

CONFIRM_LABEL = "Yes"
DENY_LABEL = "No"

CONFIRM_BUTTON_STYLE = discord.ButtonStyle.green
DENY_BUTTON_STYLE = discord.ButtonStyle.red


class Confirmation(ui.View):
    """
    A view for responding to a confirmation-based
    interaction with a confirm or deny button.
    """

    def __init__(
        self,
        interaction: discord.Interaction,
        /,
        *,
        confirmation_message: str,
        denial_message: str,
    ) -> None:
        """A view for responding to a confirmation-based
        interaction with a confirm or deny button.

        Args:
            interaction (discord.Interaction): The interaction instance.
            confirmation_message (str): The message to respond with on confirmation.
            denial_message (str): The message to respond with on denial.
        """

        super().__init__(timeout=15)  # seconds

        self.__interaction = interaction
        self.__confirm_msg = confirmation_message
        self.__deny_msg = denial_message

        self.__confirm_func: AsyncFunction | None = None
        self.__confirm_args = ()
        self.__confirm_kwargs: dict[str, Any] = {}

        self.__deny_func: AsyncFunction | None = None
        self.__deny_args = ()
        self.__deny_kwargs: dict[str, Any] = {}

    def on_confirmation(
        self,
        func: AsyncFunction | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """Set the function that will run on confirmation.

        Args:
            func (Union[AsyncFunction, None]): The function to run on confirmation.
            args (tuple[Any, ...]): The argument to pass to the function.
            kwargs (dict[str, Any]): The keyword arguments to pass to the function.
        """

        self.__confirm_func = func
        self.__confirm_args = args
        self.__confirm_kwargs = kwargs

    def on_denial(
        self,
        func: AsyncFunction | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """Set the function that will run on denial.

        Args:
            func (Union[AsyncFunction, None]): The function to run on denial.
            args (tuple[Any, ...]): The argument to pass to the function.
            kwargs (dict[str, Any]): The keyword arguments to pass to the function.
        """

        self.__deny_func = func
        self.__deny_args = args
        self.__deny_kwargs = kwargs

    @discord.ui.button(label=CONFIRM_LABEL, style=CONFIRM_BUTTON_STYLE)
    async def confirm(
        self, interaction: discord.Interaction, button: ui.Button[Confirmation]
    ) -> None:
        """This function will run on confirmation.

        Args:
            interaction (discord.Interaction): The interaction instance.
            button (ui.Button): The confirmation button.
        """

        button.disabled = True
        await interaction.response.defer()

        if self.__confirm_func is not None:
            try:
                await self.__confirm_func(*self.__confirm_args, **self.__confirm_kwargs)
            except Exception as e:
                logging.error(
                    "Confirmation function raised an error: %s", e, exc_info=True
                )

        # TODO: add a way to track if the original message with the buttons
        # was ephemeral, and match its ephemerality
        # OR
        # add params to make the confirm and/or deny messages ephemeral or not
        await interaction.followup.send(self.__confirm_msg, ephemeral=True)
        self.stop()

    @discord.ui.button(label=DENY_LABEL, style=DENY_BUTTON_STYLE)
    async def deny(
        self, interaction: discord.Interaction, button: ui.Button[Confirmation]
    ) -> None:
        """This function will run on confirmation.

        Args:
            interaction (discord.Interaction): The interaction instance.
            button (ui.Button): The confirmation button.
        """

        button.disabled = True
        await interaction.response.defer()

        if self.__deny_func is not None:
            try:
                await self.__deny_func(*self.__deny_args, **self.__deny_kwargs)
            except Exception as e:
                logging.error(
                    "Confirmation function raised an error: %s", e, exc_info=True
                )

        await interaction.followup.send(self.__deny_msg, ephemeral=True)
        self.stop()
