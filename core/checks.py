from __future__ import annotations

import discord
from discord import app_commands


def is_owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        bot = interaction.client
        owner_ids = getattr(bot, "owner_ids_config", set()) or set()
        if interaction.user.id in owner_ids:
            return True
        # Do not call bot.is_owner() here. In discord.py that can fetch
        # application_info(), which performs live HTTP during the interaction
        # check and can consume the 3-second response window.
        raise app_commands.CheckFailure("Owner-only command. Set OWNER_IDS in .env to enable this safely.")

    return app_commands.check(predicate)


def can_moderate(actor: discord.Member, target: discord.Member, guild: discord.Guild) -> tuple[bool, str]:
    if actor.id == guild.owner_id:
        return True, ""
    if target.id == guild.owner_id:
        return False, "Cannot moderate the server owner."
    if actor.top_role <= target.top_role:
        return False, "Your top role must be above the target member."
    return True, ""


def bot_can_act(bot_member: discord.Member, target: discord.Member) -> tuple[bool, str]:
    if target.top_role >= bot_member.top_role:
        return False, "Bot role must be above the target member/role."
    return True, ""
