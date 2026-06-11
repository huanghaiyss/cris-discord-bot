from __future__ import annotations

import asyncio
import logging
import sqlite3

import aiohttp
import aiosqlite
import discord
from discord import app_commands

from core.embeds import error, warning
from core.interactions import interaction_context, safe_send

log = logging.getLogger(__name__)


def _unwrap_exception(exc: BaseException) -> BaseException:
    if isinstance(exc, app_commands.CommandInvokeError):
        return getattr(exc, "original", exc) or exc
    return getattr(exc, "original", exc) or exc


async def handle_app_command_error(
    interaction: discord.Interaction,
    exc: app_commands.AppCommandError,
) -> None:
    """Global slash-command error handler that must never raise.

    Discord interactions are time-sensitive. This handler uses safe_send so a
    timed-out/unknown interaction or network failure is logged, not escalated
    into a secondary "Task exception was never retrieved".
    """
    try:
        original = _unwrap_exception(exc)
        ctx = interaction_context(interaction)
        log.warning(
            "App command error: command=%s guild_id=%s user_id=%s exc=%s original=%s",
            ctx["command"],
            ctx["guild_id"],
            ctx["user_id"],
            type(exc).__name__,
            type(original).__name__,
        )

        if isinstance(exc, app_commands.MissingPermissions):
            await safe_send(interaction, embed=error("You do not have permission to use that command."), ephemeral=True)
            return

        if isinstance(exc, app_commands.BotMissingPermissions):
            await safe_send(interaction, embed=error("I am missing permissions required for that action."), ephemeral=True)
            return

        if isinstance(exc, app_commands.CommandOnCooldown):
            await safe_send(interaction, embed=warning(f"Try again in {exc.retry_after:.0f}s."), ephemeral=True)
            return

        if isinstance(exc, app_commands.TransformerError):
            await safe_send(interaction, embed=error("Bad input. Check the command options."), ephemeral=True)
            return

        if isinstance(exc, app_commands.CheckFailure):
            message = str(exc) or "You cannot use that command."
            await safe_send(interaction, embed=error(message), ephemeral=True)
            return

        if isinstance(original, discord.NotFound):
            code = getattr(original, "code", None)
            if code == 10062:
                log.warning("Unknown/expired interaction while handling command: %s", ctx)
                return
            await safe_send(interaction, embed=error("Discord could not find that interaction or resource."), ephemeral=True)
            return

        if isinstance(original, (aiosqlite.OperationalError, sqlite3.OperationalError)):
            if "locked" in str(original).lower():
                await safe_send(interaction, embed=error("Database is busy. Try again shortly."), ephemeral=True)
            else:
                await safe_send(interaction, embed=error("Database error. It has been logged."), ephemeral=True)
            return

        if isinstance(original, (aiosqlite.Error, sqlite3.Error)):
            await safe_send(interaction, embed=error("Database error. It has been logged."), ephemeral=True)
            return

        if isinstance(original, discord.HTTPException):
            await safe_send(
                interaction,
                embed=error("Discord rejected that action. Check permissions, role hierarchy, and channel access."),
                ephemeral=True,
            )
            return

        if isinstance(original, (aiohttp.ClientError, asyncio.TimeoutError)):
            await safe_send(interaction, embed=error("Network timeout talking to Discord. Try again."), ephemeral=True)
            return

        if isinstance(exc, app_commands.AppCommandError):
            await safe_send(interaction, embed=error("Command failed. It has been logged."), ephemeral=True)
            return

        await safe_send(interaction, embed=error("Unexpected error. It has been logged."), ephemeral=True)
    except Exception as handler_exc:
        ctx = interaction_context(interaction)
        log.exception(
            "Error handler failed but was suppressed: command=%s guild_id=%s user_id=%s exc=%s",
            ctx["command"],
            ctx["guild_id"],
            ctx["user_id"],
            type(handler_exc).__name__,
        )
