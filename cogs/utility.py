import asyncio
import logging
import platform

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from core.embeds import make_embed
from core.interactions import interaction_context, safe_defer, safe_send

log = logging.getLogger(__name__)


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="utility", description="Server utilities")

    @group.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        if not await safe_defer(interaction, ephemeral=False):
            return
        await safe_send(interaction, embed=make_embed("Pong", f"{self.bot.latency * 1000:.0f} ms", "info"), ephemeral=False)

    @group.command(name="userinfo")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member | None = None):
        if not await safe_defer(interaction, ephemeral=False):
            return
        target = user or interaction.user
        await safe_send(
            interaction,
            embed=make_embed(
                "User Info",
                f'{target.mention}\nID: `{target.id}`\nJoined: {getattr(target, "joined_at", None)}',
                "info",
            ),
            ephemeral=False,
        )

    @group.command(name="serverinfo")
    async def serverinfo(self, interaction: discord.Interaction):
        if not await safe_defer(interaction, ephemeral=False):
            return
        guild = interaction.guild
        if guild is None:
            await safe_send(interaction, embed=make_embed("Server Info", "This command only works in a server.", "error"), ephemeral=True)
            return
        await safe_send(
            interaction,
            embed=make_embed("Server Info", f"{guild.name}\nMembers: {guild.member_count}\nID: `{guild.id}`", "info"),
            ephemeral=False,
        )

    @group.command(name="avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.User | None = None):
        if not await safe_defer(interaction, ephemeral=False):
            return
        target = user or interaction.user
        embed = make_embed("Avatar", target.mention, "info")
        embed.set_image(url=target.display_avatar.url)
        await safe_send(interaction, embed=embed, ephemeral=False)

    @group.command(name="botinfo")
    async def botinfo(self, interaction: discord.Interaction):
        if not await safe_defer(interaction, ephemeral=False):
            return
        await safe_send(
            interaction,
            embed=make_embed(
                "Bot Info",
                f"discord.py {discord.__version__}\nPython {platform.python_version()}\nGuilds: {len(self.bot.guilds)}",
                "info",
            ),
            ephemeral=False,
        )

    @group.command(name="channelinfo")
    async def channelinfo(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None):
        if not await safe_defer(interaction, ephemeral=False):
            return
        target = channel or interaction.channel
        await safe_send(
            interaction,
            embed=make_embed(
                "Channel Info",
                f'{target.mention}\nID: `{target.id}`\nTopic: {getattr(target, "topic", None)}',
                "info",
            ),
            ephemeral=False,
        )

    @group.command(name="roleinfo")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        if not await safe_defer(interaction, ephemeral=False):
            return
        await safe_send(
            interaction,
            embed=make_embed("Role Info", f"{role.mention}\nID: `{role.id}`\nMembers: {len(role.members)}", "info"),
            ephemeral=False,
        )

    @group.command(name="invite_info")
    async def invite_info(self, interaction: discord.Interaction, invite: str):
        if not await safe_defer(interaction, ephemeral=True):
            return
        try:
            inv = await self.bot.fetch_invite(invite)
            text = f"Guild: {inv.guild}\nChannel: {inv.channel}\nUses: {inv.uses}"
        except discord.HTTPException:
            text = "Invite not found or not accessible."
        await safe_send(interaction, embed=make_embed("Invite Info", text, "info"), ephemeral=True)

    @group.command(name="poll")
    async def poll(self, interaction: discord.Interaction, question: str, options: str):
        opts = [o.strip() for o in options.split("|") if o.strip()][:10]
        if len(opts) < 2:
            await safe_send(interaction, embed=make_embed("Poll", "Provide at least two options separated by `|`.", "error"), ephemeral=True)
            return
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        embed = make_embed(
            "Poll",
            question + "\n\n" + "\n".join(f"{emojis[n]} {option}" for n, option in enumerate(opts)),
            "info",
        )
        if not await safe_defer(interaction, ephemeral=False):
            return
        try:
            sent = await interaction.followup.send(embed=embed, wait=True)
            for n in range(len(opts)):
                await sent.add_reaction(emojis[n])
        except (discord.NotFound, discord.HTTPException, aiohttp.ClientError, asyncio.TimeoutError) as exc:
            log.warning("POLL_SEND_FAILED %s exc=%s", interaction_context(interaction), type(exc).__name__)


async def setup(bot):
    await bot.add_cog(Utility(bot))
