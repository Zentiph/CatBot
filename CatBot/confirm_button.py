"""
confirm_button.py
A confirmation button to be used with CatBot
affirmation-needing commands.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, Union

import discord
from discord import ui

AsyncFunction = Callable[..., Awaitable[Any]]


class ConfirmButton(ui.View):
    """
    Base discord.ui.View for responding to a command with
    a confirm or deny button.
    """

    def __init__(
        self, interaction: discord.Interaction, confirm_msg: str, deny_msg: str
    ) -> None:
        """
        Base discord.ui.View for responding to a command with
        a confirm or deny button.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param confirm_msg: Message to respond with on action confirmation.
        :type confirm_msg: str
        :param deny_msg: Message to respond with on action denial.
        :type deny_msg: str
        """

        super().__init__(timeout=30)  # Buttons will expire after 30 seconds
        self.interaction = interaction
        self.confirm_msg = confirm_msg
        self.deny_msg = deny_msg

        self._confirm_func: Union[AsyncFunction, None] = None
        self._confirm_args = ()
        self._confirm_kwargs: Dict[Any, Any] = {}

    def on_confirmation(
        self, func: Union[AsyncFunction, None], *args: Any, **kwargs: Any
    ) -> None:
        """
        Set the function to run on confirmation.

        :param func: Function to run on confirmation.
        :type func: Union[AsyncFunction, None]
        :param args: Arguments to pass to `func`.
        :type args: Any
        :param kwargs: Keyword arguments to pass to `func`.
        :type kwargs: Any
        """

        self._confirm_func = func
        self._confirm_args = args
        self._confirm_kwargs = kwargs

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: ui.Button
    ) -> None:
        """
        Run on confirmation.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param button: Yes button
        :type button: ui.Button
        """

        button.disabled = True
        await interaction.response.defer()

        if self._confirm_func is not None:
            try:
                await self._confirm_func(*self._confirm_args, **self._confirm_kwargs)
                await interaction.followup.send(self.confirm_msg, ephemeral=True)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logging.error(
                    "Yes button confirmation function raised an error: %s",
                    e,
                    exc_info=True,
                )

        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: ui.Button) -> None:
        """
        Run on denial.

        :param interaction: Interaction instance
        :type interaction: discord.Interaction
        :param button: No button
        :type button: ui.Button
        """

        button.disabled = True
        await interaction.response.send_message(self.deny_msg, ephemeral=True)
        self.stop()
