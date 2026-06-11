from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Any

import aiohttp
import discord

log = logging.getLogger(__name__)

_SECRETISH_RE = re.compile(r"[A-Za-z0-9_\-]{24,}\.[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{20,}")
_MAX_VALUE_LEN = 160


def _safe_text(value: Any) -> str | int | float | bool | None:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if _SECRETISH_RE.search(text):
        return "[redacted-token-like-value]"
    if len(text) > _MAX_VALUE_LEN:
        return text[:_MAX_VALUE_LEN] + "…"
    return text


def _interaction_data(interaction: discord.Interaction) -> dict[str, Any]:
    raw = getattr(interaction, "data", None)
    return raw if isinstance(raw, dict) else {}


def _option_summary(options: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for option in options or []:
        item: dict[str, Any] = {
            "name": option.get("name"),
            "type": option.get("type"),
        }
        if "value" in option:
            item["value"] = _safe_text(option.get("value"))
        if "options" in option:
            item["options"] = _option_summary(option.get("options"))
        summary.append(item)
    return summary


def interaction_context(interaction: discord.Interaction) -> dict[str, Any]:
    """Return safe interaction metadata for logs.

    Never include tokens, interaction callback URLs, or webhook URLs here.
    """
    command = getattr(interaction, "command", None)
    data = _interaction_data(interaction)
    user = getattr(interaction, "user", None)
    guild = getattr(interaction, "guild", None)
    channel = getattr(interaction, "channel", None)
    command_name = getattr(command, "qualified_name", None) or data.get("name") or getattr(command, "name", None)
    return {
        "interaction_id": getattr(interaction, "id", None),
        "type": getattr(getattr(interaction, "type", None), "name", str(getattr(interaction, "type", None))),
        "command": command_name or "unknown",
        "custom_id": data.get("custom_id"),
        "guild_id": interaction.guild_id,
        "guild": _safe_text(getattr(guild, "name", None)),
        "channel_id": getattr(channel, "id", getattr(interaction, "channel_id", None)),
        "channel": _safe_text(getattr(channel, "name", None)),
        "user_id": getattr(user, "id", None),
        "user": _safe_text(str(user)) if user else None,
        "response_done": interaction.response.is_done(),
        "options": _option_summary(data.get("options")),
    }


def log_interaction_received(interaction: discord.Interaction) -> None:
    log.info("INTERACTION_RECEIVED %s", interaction_context(interaction))


def log_interaction_check(interaction: discord.Interaction) -> None:
    log.info("COMMAND_CHECK_START %s", interaction_context(interaction))


def log_command_callback_start(interaction: discord.Interaction) -> float:
    started = time.monotonic()
    setattr(interaction, "_everything_bot_command_started", started)
    log.info("COMMAND_CALLBACK_START %s", interaction_context(interaction))
    return started


def log_command_callback_end(interaction: discord.Interaction, started: float | None = None) -> None:
    started = started or getattr(interaction, "_everything_bot_command_started", None)
    elapsed_ms = None if started is None else round((time.monotonic() - started) * 1000, 1)
    ctx = interaction_context(interaction)
    ctx["elapsed_ms"] = elapsed_ms
    log.info("COMMAND_CALLBACK_END %s", ctx)


def _exception_summary(exc: BaseException) -> dict[str, Any]:
    summary: dict[str, Any] = {"exc_type": type(exc).__name__}
    code = getattr(exc, "code", None)
    status = getattr(exc, "status", None)
    if code is not None:
        summary["code"] = code
    if status is not None:
        summary["status"] = status
    # Avoid str(exc) for aiohttp/Discord callback errors because it can contain
    # the interaction callback URL/token. Type/status/code are enough here.
    return summary


async def safe_defer(
    interaction: discord.Interaction,
    *,
    ephemeral: bool = True,
    thinking: bool = True,
) -> bool:
    """Safely defer an interaction response."""
    try:
        if interaction.response.is_done():
            log.info("INTERACTION_DEFER_SKIPPED_ALREADY_ACKED %s", interaction_context(interaction))
            return True
        await interaction.response.defer(ephemeral=ephemeral, thinking=thinking)
        ctx = interaction_context(interaction)
        ctx.update({"ephemeral": ephemeral, "thinking": thinking})
        log.info("INTERACTION_DEFER_OK %s", ctx)
        return True
    except discord.NotFound as exc:
        ctx = interaction_context(interaction)
        ctx.update(_exception_summary(exc))
        if getattr(exc, "code", None) == 10062:
            log.warning("INTERACTION_DEFER_EXPIRED %s", ctx)
        else:
            log.warning("INTERACTION_DEFER_NOT_FOUND %s", ctx)
        return False
    except (discord.HTTPException, aiohttp.ClientError, asyncio.TimeoutError) as exc:
        ctx = interaction_context(interaction)
        ctx.update(_exception_summary(exc))
        log.warning("INTERACTION_DEFER_FAILED %s", ctx)
        return False
    except Exception as exc:  # defensive: this helper must never crash command tasks
        ctx = interaction_context(interaction)
        ctx.update(_exception_summary(exc))
        log.exception("INTERACTION_DEFER_UNEXPECTED_FAILURE %s", ctx)
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
    """Safely send an interaction response or followup."""
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

        mode = "followup" if interaction.response.is_done() else "initial_response"
        if interaction.response.is_done():
            await interaction.followup.send(**params)
        else:
            await interaction.response.send_message(**params)
        ctx = interaction_context(interaction)
        ctx.update({"mode": mode, "ephemeral": ephemeral, "has_content": content is not None, "has_embed": embed is not None, "has_embeds": embeds is not None})
        log.info("INTERACTION_SEND_OK %s", ctx)
        return True
    except discord.NotFound as exc:
        ctx = interaction_context(interaction)
        ctx.update(_exception_summary(exc))
        if getattr(exc, "code", None) == 10062:
            log.warning("INTERACTION_SEND_EXPIRED %s", ctx)
        else:
            log.warning("INTERACTION_SEND_NOT_FOUND %s", ctx)
        return False
    except (discord.HTTPException, aiohttp.ClientError, asyncio.TimeoutError) as exc:
        ctx = interaction_context(interaction)
        ctx.update(_exception_summary(exc))
        log.warning("INTERACTION_SEND_FAILED %s", ctx)
        return False
    except Exception as exc:  # defensive: never create a second task exception
        ctx = interaction_context(interaction)
        ctx.update(_exception_summary(exc))
        log.exception("INTERACTION_SEND_UNEXPECTED_FAILURE %s", ctx)
        return False
