from __future__ import annotations
import logging, sqlite3
import aiosqlite, discord
from discord import app_commands
from core.embeds import error, warning
log = logging.getLogger(__name__)

async def send_safe(interaction: discord.Interaction, embed: discord.Embed, ephemeral: bool=True) -> None:
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    except discord.HTTPException:
        log.exception('Failed to send error response')

async def handle_app_command_error(interaction: discord.Interaction, exc: app_commands.AppCommandError) -> None:
    original = getattr(exc, 'original', exc)
    if isinstance(exc, app_commands.MissingPermissions):
        await send_safe(interaction, error('You do not have permission to use that command.')); return
    if isinstance(exc, app_commands.BotMissingPermissions):
        await send_safe(interaction, error('I am missing permissions required for that action.')); return
    if isinstance(exc, app_commands.CommandOnCooldown):
        await send_safe(interaction, warning(f'Try again in {exc.retry_after:.0f}s.')); return
    if isinstance(exc, (app_commands.TransformerError, app_commands.BadArgument)):
        await send_safe(interaction, error('Bad input. Check the command options.')); return
    if isinstance(original, (aiosqlite.OperationalError, sqlite3.OperationalError)) and 'locked' in str(original).lower():
        log.exception('Database locked during command')
        await send_safe(interaction, error('Database is busy. Try again shortly.')); return
    if isinstance(original, discord.HTTPException):
        log.exception('Discord HTTP error')
        await send_safe(interaction, error('Discord rejected that action. Check permissions and hierarchy.')); return
    log.exception('Unhandled app command error', exc_info=exc)
    await send_safe(interaction, error('Unexpected error. It has been logged.'))
