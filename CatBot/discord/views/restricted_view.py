"""A restricted ui View that only the interaction user can interact with."""

from abc import ABC
from collections.abc import Callable, Sequence

import discord
from discord.utils import MISSING

from ..interaction import report
from ..ui.emoji import Status

__author__ = "Gavin Borne"
__license__ = "MIT"

Check = Callable[[discord.Interaction], bool]


class RestrictedView(ABC, discord.ui.View):
    """A view that restricts people except the interaction user from using it."""

    def __init__(
        self,
        *,
        user: discord.abc.User,
        timeout: float | None = 60.0,
        deny_message: str = "You can't interact with another user's embed!",
        deny_status: Status = Status.FAILURE,
        ephemeral: bool = True,
        allow: Check | None = None,
    ) -> None:
        """A view that restricts people except the interaction user from using it.

        Args:
            user (discord.abc.User): The user with interaction access.
            timeout (float | None, optional): The timeout of the view (in seconds).
                Defaults to 60.0.
            deny_message (str, optional): The message to give when denying access to
                unauthorized users. Defaults to "You can't interact with another user's
                embed!"
            deny_status (Status, optional): The response status to give when denying
                access to unauthorized users.
            ephemeral (bool, optional): Whether the deny response should be ephemeral.
                Defaults to True.
            allow (Check | None, optional): An optional predicate to allow additional
                users to interact with the view. Defaults to None.
        """
        super().__init__(timeout=timeout)
        self.__user_id = user.id
        self.__deny_message = deny_message
        self.__deny_status = deny_status
        self.__deny_ephemeral = ephemeral
        self.__allow = allow

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        """On each interaction instance, check that the user is authorized.

        Args:
            interaction (discord.Interaction): The interaction instance.

        Returns:
            bool: Whether the user who interacted is authorized to interact with this
                view.
        """
        ok_owner = interaction.user.id == self.__user_id
        ok_extra = self.__allow(interaction) if self.__allow else False

        if not (ok_owner or ok_extra):
            await report(
                interaction,
                self.__deny_message,
                self.__deny_status,
                ephemeral=self.__deny_ephemeral,
            )
            return False
        return True

    async def respond(
        self,
        interaction: discord.Interaction,
        /,
        content: str | None = None,
        *,
        ephemeral: bool = True,
        embed: discord.Embed = MISSING,
        embeds: Sequence[discord.Embed] = MISSING,
        view: discord.ui.View = MISSING,
        file: discord.File = MISSING,
        files: Sequence[discord.File] = MISSING,
        delete_after: float = MISSING,
    ) -> None:
        """Send a message in response to an interaction, handling double-responds.

        This helper prefers `interaction.response.send_message(...)`. If the interaction
        has already been responded to (i.e. `discord.InteractionResponded` is raised),
        it falls back to `interaction.followup.send(...)`.

        Notes:
            - `discord.InteractionResponse.send_message` allows `content=None`, but
              `discord.Webhook.send` (used by followups) requires a string. When
              `content` is None, this helper omits the content argument for the
              followup case.
            - Parameters default to `discord.utils.MISSING` where appropriate so they
              are only sent to Discord if explicitly provided.

        Args:
            interaction (discord.Interaction): The interaction instance to respond to.
            content (str | None, optional): The message content. If None, content is
                omitted for followup sends. Defaults to None.
            ephemeral (bool, optional): Whether the message should be ephemeral.
                Defaults to True.
            embed (discord.Embed, optional): A single embed to include. Defaults to
                `MISSING`.
            embeds (Sequence[discord.Embed], optional): Multiple embeds to include.
                Defaults to `MISSING`.
            view (discord.ui.View, optional): A view to attach to the message. Defaults
                to `MISSING`.
            file (discord.File, optional): A single file to include. Defaults to
                `MISSING`.
            files (Sequence[discord.File], optional): Multiple files to include.
                Defaults to `MISSING`.
            delete_after (float, optional): Delete the message after this many seconds.
                Defaults to `MISSING`.

        Raises:
            discord.HTTPException: If Discord rejects the request.
            discord.Forbidden: If the bot lacks permissions to send the message.
        """
        try:
            await interaction.response.send_message(
                content,
                ephemeral=ephemeral,
                embed=embed,
                embeds=embeds,
                view=view,
                file=file,
                files=files,
                delete_after=delete_after,
            )
        except discord.InteractionResponded:
            if content is None:
                await interaction.followup.send(
                    ephemeral=ephemeral,
                    embed=embed,
                    embeds=embeds,
                    view=view,
                    file=file,
                    files=files,
                )
            else:
                await interaction.followup.send(
                    content,
                    ephemeral=ephemeral,
                    embed=embed,
                    embeds=embeds,
                    view=view,
                    file=file,
                    files=files,
                )

    async def edit(
        self,
        interaction: discord.Interaction,
        /,
        *,
        content: str | None = None,
        embed: discord.Embed = MISSING,
        embeds: Sequence[discord.Embed] = MISSING,
        attachments: Sequence[discord.Attachment | discord.File] = MISSING,
        view: discord.ui.View = MISSING,
        allowed_mentions: discord.AllowedMentions = MISSING,
    ) -> None:
        """Edit the message associated with an interaction, handling response state.

        This helper prefers `interaction.response.edit_message(...)`. If the interaction
        has already been responded to (i.e. `discord.InteractionResponded` is raised),
        it falls back to `interaction.edit_original_response(...)`.

        Notes:
            - Use `attachments` to replace the message's attachments. If you want to
              keep existing attachments, you must include them again (Discord treats
              this as a replacement list).
            - Parameters default to `discord.utils.MISSING` where appropriate so they
              are only sent to Discord if explicitly provided.

        Args:
            interaction (discord.Interaction): The interaction instance whose message
                should be edited.
            content (str | None, optional): New message content. Defaults to None.
            embed (discord.Embed, optional): A single embed to set. Defaults to
                `MISSING`.
            embeds (Sequence[discord.Embed], optional): Multiple embeds to set.
                Defaults to `MISSING`.
            attachments (Sequence[discord.Attachment | discord.File], optional): New
                attachments for the message. Defaults to `MISSING`.
            view (discord.ui.View, optional): A view to attach/update on the message.
                Defaults to `MISSING`.
            allowed_mentions (discord.AllowedMentions, optional): Controls mention
                parsing for the edited message. Defaults to `MISSING`.

        Raises:
            discord.HTTPException: If Discord rejects the edit.
            discord.Forbidden: If the bot lacks permissions to edit the message.
        """
        try:
            await interaction.response.edit_message(
                content=content,
                embed=embed,
                embeds=embeds,
                attachments=attachments,
                view=view,
                allowed_mentions=allowed_mentions,
            )
        except discord.InteractionResponded:
            await interaction.edit_original_response(
                content=content,
                embed=embed,
                embeds=embeds,
                attachments=attachments,
                view=view,
                allowed_mentions=allowed_mentions,
            )


class RestrictedModal(ABC, discord.ui.Modal):
    """A modal that restricts people except the interaction user from using it."""

    def __init__(self, view: RestrictedView, *, title: str) -> None:
        """A modal that restricts people except the interaction user from using it.

        Args:
            view (RestrictedView): The restricted view which this modal is part of.
            title (str): The title of the modal.
        """
        super().__init__(title=title)
        self.__view = view

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        """Validate that the user from the interaction is this embed's user.

        Args:
            interaction (discord.Interaction): The interaction instance.

        Returns:
            bool: Whether this user is validated.
        """
        return await self.__view.interaction_check(interaction)
