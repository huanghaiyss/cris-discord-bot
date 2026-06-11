from __future__ import annotations

import logging

import discord
from discord import app_commands

from core.interactions import interaction_context, log_interaction_check

log = logging.getLogger(__name__)


class LoggedCommandTree(app_commands.CommandTree):
    """CommandTree that logs app-command dispatch before command checks run."""

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        log_interaction_check(interaction)
        return True

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError, /) -> None:
        # setup_hook replaces this with core.errors.handle_app_command_error.
        # Keep a safe fallback if setup fails before assignment.
        ctx = interaction_context(interaction)
        log.exception("COMMAND_TREE_ERROR_FALLBACK %s exc=%s", ctx, type(error).__name__, exc_info=error)
