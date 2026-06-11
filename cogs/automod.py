import discord
from discord import app_commands
from discord.ext import commands

from core.embeds import make_embed, success
from core.interactions import safe_defer, safe_send
from services.automod_service import AutomodService


class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.svc = AutomodService(bot.db)

    group = app_commands.Group(name="automod", description="Defensive automod")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if not msg.guild or msg.author.bot or (isinstance(msg.author, discord.Member) and msg.author.guild_permissions.manage_messages):
            return
        conf = await self.svc.config(msg.guild.id)
        if not int(conf["enabled"]):
            return
        violation = self.svc.inspect_message(msg.guild.id, msg.author.id, msg.content, len(msg.mentions), conf)
        if violation:
            try:
                await msg.delete()
            except discord.HTTPException:
                pass
            await self.svc.record_violation(msg.guild.id, msg.author.id, violation, msg.content, "delete")

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if msg.guild and msg.mentions and not msg.author.bot:
            await self.svc.record_violation(msg.guild.id, msg.author.id, "possible_ghost_ping", msg.content, "log")

    @group.command(name="status")
    async def status(self, i: discord.Interaction):
        if not await safe_defer(i, ephemeral=True):
            return
        conf = await self.svc.config(i.guild_id)
        await safe_send(i, embed=make_embed("Automod", str(dict(conf)), "warning"), ephemeral=True)

    async def _flag(self, i: discord.Interaction, key: str, val: int):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.svc.set_flag(i.guild_id, key, val)
        await safe_send(i, embed=success(f"{key} set to {val}"), ephemeral=True)

    @group.command(name="enable")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, i: discord.Interaction):
        await self._flag(i, "enabled", 1)

    @group.command(name="disable")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self, i: discord.Interaction):
        await self._flag(i, "enabled", 0)

    @group.command(name="config")
    async def config(self, i: discord.Interaction):
        await self.status(i)

    @group.command(name="set_log_channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, i: discord.Interaction, channel: discord.TextChannel):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.svc.set_int(i.guild_id, "log_channel_id", channel.id)
        await safe_send(i, embed=success("Automod log saved."), ephemeral=True)

    @group.command(name="set_spam_threshold")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_spam_threshold(self, i: discord.Interaction, value: app_commands.Range[int, 3, 20]):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.svc.set_int(i.guild_id, "spam_threshold", value)
        await safe_send(i, embed=success("Spam threshold saved."), ephemeral=True)

    @group.command(name="set_mention_threshold")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_mention_threshold(self, i: discord.Interaction, value: app_commands.Range[int, 3, 50]):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.svc.set_int(i.guild_id, "mention_threshold", value)
        await safe_send(i, embed=success("Mention threshold saved."), ephemeral=True)

    @group.command(name="toggle_invite_filter")
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_invite_filter(self, i: discord.Interaction, enabled: bool):
        await self._flag(i, "invite_filter", int(enabled))

    @group.command(name="toggle_link_filter")
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_link_filter(self, i: discord.Interaction, enabled: bool):
        await self._flag(i, "link_filter", int(enabled))

    @group.command(name="panic_enable")
    @app_commands.checks.has_permissions(administrator=True)
    async def panic_enable(self, i: discord.Interaction):
        await self._flag(i, "panic_mode", 1)

    @group.command(name="panic_disable")
    @app_commands.checks.has_permissions(administrator=True)
    async def panic_disable(self, i: discord.Interaction):
        await self._flag(i, "panic_mode", 0)


async def setup(bot):
    await bot.add_cog(Automod(bot))
