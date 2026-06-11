from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import discord

log = logging.getLogger(__name__)


def interaction_context(interaction: discord.Interaction) -> dict[str, Any]:
    """Return safe interaction metadata for logs.

    Never include tokens, interaction callback URLs, or webhook URLs here.
    """
    command = getattr(interaction, "command", None)
    command_name = getattr(command, "qualified_name", None) or getattr(command, "name", None)
    return {
        "command": command_name or "unknown",
        "guild_id": interaction.guild_id,
        "user_id": getattr(interaction.user, "id", None),
    }


async def safe_defer(
    interaction: discord.Interaction,
    *,
    ephemeral: bool = True,
    thinking: bool = True,
) -> bool:
    """Safely defer an interaction response.

    Returns True if the interaction is now acknowledged/already acknowledged.
    Returns False if Discord rejected or the network failed. Failures are logged
    and never re-raised so command tasks do not produce secondary exceptions.
    """
    try:
        if interaction.response.is_done():
            return True
        await interaction.response.defer(ephemeral=ephemeral, thinking=thinking)
        return True
    except discord.NotFound as exc:
        # Usually 10062 Unknown interaction: the three-second ACK window expired
        # or Discord invalidated the token. Nothing useful can be sent afterward.
        code = getattr(exc, "code", None)
        if code == 10062:
            log.warning("Interaction expired before defer: %s", interaction_context(interaction))
        else:
            log.warning("Interaction not found during defer: %s code=%s", interaction_context(interaction), code)
        return False
    except (discord.HTTPException, aiohttp.ClientError, asyncio.TimeoutError) as exc:
        log.warning(
            "Failed to defer interaction: %s exc=%s",
            interaction_context(interaction),
            type(exc).__name__,
            exc_info=True,
        )
        return False
    except Exception as exc:  # defensive: this helper must never crash command tasks
        log.exception(
            "Unexpected failure while deferring interaction: %s exc=%s",
            interaction_context(interaction),
            type(exc).__name__,
        )
        return False


async def safe_send(
    interaction: discord.Interaction,
    content: str | None = None,
    *,
    embed: discord.Embed | None = None,
    embeds: list[discord.Embed] | None = None,
    ephemeral: bool = True,
    **kwargs: Any,
) -> bool:
    """Safely send an interaction response or followup.

    Uses the initial response if the interaction has not been acknowledged yet;
    otherwise uses followup.send. Network/API failures are logged and swallowed.
    """
    try:
        params: dict[str, Any] = {"ephemeral": ephemeral, **kwargs}
        if content is not None:
            params["content"] = content
        if embed is not None and embeds is not None:
            raise TypeError("safe_send received both embed and embeds")
        if embed is not None:
            params["embed"] = embed
        if embeds is not None:
            params["embeds"] = embeds

        if interaction.response.is_done():
            await interaction.followup.send(**params)
        else:
            await interaction.response.send_message(**params)
        return True
    except discord.NotFound as exc:
        code = getattr(exc, "code", None)
        if code == 10062:
            log.warning("Interaction expired before send: %s", interaction_context(interaction))
        else:
            log.warning("Interaction not found during send: %s code=%s", interaction_context(interaction), code)
        return False
    except (discord.HTTPException, aiohttp.ClientError, asyncio.TimeoutError) as exc:
        log.warning(
            "Failed to send interaction response: %s exc=%s",
            interaction_context(interaction),
            type(exc).__name__,
            exc_info=True,
        )
        return False
    except Exception as exc:  # defensive: never create a second task exception
        log.exception(
            "Unexpected failure while sending interaction response: %s exc=%s",
            interaction_context(interaction),
            type(exc).__name__,
        )
        return False
