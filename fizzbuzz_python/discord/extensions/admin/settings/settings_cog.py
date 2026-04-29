"""Guild settings commands."""

from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from .....db.settings import settings_manager
from .....util.log_handler import cog_setup_log_msg, log_app_command
from ....checks import get_guild, owner_only
from ....interaction import build_response_embed, report, safe_send
from ....ui.emoji import Status
from ...public.help.help_registrator import help_info

__author__ = "Gavin Borne"
__license__ = "MIT"

AdminRoleAction = Literal["add", "remove", "list"]

# TODO: see how to make admin commands hide from regular users in auto generated
# menu in discord


class SettingsCog(commands.Cog, name="Guild Settings"):
    """Cog containing guild settings updaters."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create the SettingsCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        # TODO: see if type(self).__name__ can be automated inside cog_setup_log_msg
        # with inspect or something similar
        # (or at least allow to just pass self or type(self))
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(
        name="adminrole", description="Update the admin roles for a guild"
    )
    @app_commands.describe(action="The action to perform", role="The role to update")
    @owner_only()
    @help_info(
        "Guild Settings",
        examples=(
            "/adminrole action:add role:@Admin",
            "/adminrole action:remove role:@Untrustworthy",
            "/adminrole action:list",
        ),
        notes=("Only the guild owner can execute this command.",),
    )
    async def admin_role(
        self,
        interaction: discord.Interaction,
        action: AdminRoleAction,
        role: discord.Role | None = None,
    ) -> None:
        """Add, remove, or list admin roles in a guild."""
        log_app_command(interaction)

        guild = get_guild(interaction)
        admin_role_ids = await settings_manager.get_admin_role_ids(guild.id)

        if action in {"add", "remove"}:
            if role is None:
                await report(
                    interaction,
                    "You must provide a role to add or remove!",
                    Status.FAILURE,
                )
                return

            if action == "add":
                if role.id in admin_role_ids:
                    await report(
                        interaction,
                        "This role is already an admin role!",
                        Status.FAILURE,
                    )
                    return

                await settings_manager.add_admin_role_id(guild.id, role.id)
                await report(
                    interaction,
                    f"Successfully added {role.mention} as an admin role!",
                    Status.SUCCESS,
                )
                return

            # else "remove"
            if role.id not in admin_role_ids:
                await report(
                    interaction, "This role is not an admin role!", Status.FAILURE
                )
                return

            await settings_manager.remove_admin_role_id(guild.id, role.id)
            await report(
                interaction,
                f"Successfully removed {role.mention} as an admin role!",
                Status.SUCCESS,
            )
            return

        # else "list"
        embed, icon = build_response_embed(
            title="Admin Roles",
            description="Here's a list of admin roles for this server.",
        )

        for rid in admin_role_ids:
            role = guild.get_role(rid)
            if role is None:
                # role was deleted, remove from DB
                await settings_manager.remove_admin_role_id(guild.id, rid)
                continue

            embed.add_field(name=role.mention, value=f"ID: {rid}")

        await safe_send(interaction, embed=embed, file=icon)


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(SettingsCog(bot))
