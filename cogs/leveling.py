import random

import discord
from discord import app_commands
from discord.ext import commands

from core.constants import MESSAGE_XP_MAX, MESSAGE_XP_MIN
from core.embeds import make_embed, success
from core.interactions import safe_defer, safe_send
from services.leveling_service import LevelingService, xp_for_level


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.svc = LevelingService(bot.db)

    group = app_commands.Group(name="level", description="XP and levels")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if not msg.guild or msg.author.bot:
            return
        conf = await self.bot.db.fetchone("SELECT leveling_enabled, level_channel_id FROM guild_config WHERE guild_id=?", (msg.guild.id,))
        if conf and not int(conf["leveling_enabled"]):
            return
        res = await self.svc.add_xp(msg.guild.id, msg.author.id, random.randint(MESSAGE_XP_MIN, MESSAGE_XP_MAX), cooldown=True)
        if res and res.leveled_up:
            ch = msg.guild.get_channel(conf["level_channel_id"]) if conf and conf["level_channel_id"] else msg.channel
            try:
                await ch.send(embed=make_embed("Level up!", f"{msg.author.mention} reached level **{res.level}**.", "leveling"))
            except discord.HTTPException:
                pass
            rows = await self.bot.db.fetchall("SELECT role_id FROM level_rewards WHERE guild_id=? AND level<=?", (msg.guild.id, res.level))
            for row in rows:
                role = msg.guild.get_role(row["role_id"])
                if role and isinstance(msg.author, discord.Member) and msg.guild.me.top_role > role:
                    try:
                        await msg.author.add_roles(role, reason="Level reward")
                    except discord.HTTPException:
                        pass

    @group.command(name="rank")
    async def rank(self, i: discord.Interaction, user: discord.Member | None = None):
        if not await safe_defer(i, ephemeral=False):
            return
        u = user or i.user
        row = await self.svc.rank(i.guild_id, u.id)
        await safe_send(i, embed=make_embed("Rank", f'{u.mention}\nLevel: **{row["level"]}**\nXP: **{row["xp"]}/{xp_for_level(int(row["level"]) + 1)}**', "leveling"), ephemeral=False)

    @group.command(name="leaderboard")
    async def leaderboard(self, i: discord.Interaction):
        if not await safe_defer(i, ephemeral=False):
            return
        rows = await self.svc.leaderboard(i.guild_id)
        text = "\n".join(f'{n + 1}. <@{r["user_id"]}> — L{r["level"]} ({r["xp"]} XP)' for n, r in enumerate(rows)) or "No XP yet."
        await safe_send(i, embed=make_embed("Level Leaderboard", text, "leveling"), ephemeral=False)

    @group.command(name="set_channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(self, i: discord.Interaction, channel: discord.TextChannel):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.bot.db.execute("INSERT INTO guild_config(guild_id,level_channel_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET level_channel_id=excluded.level_channel_id", (i.guild_id, channel.id))
        await safe_send(i, embed=success(f"Level channel: {channel.mention}"), ephemeral=True)

    @group.command(name="set_reward")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_reward(self, i: discord.Interaction, level: app_commands.Range[int, 1, 1000], role: discord.Role):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.bot.db.execute("INSERT INTO level_rewards(guild_id,level,role_id) VALUES (?,?,?) ON CONFLICT(guild_id,level) DO UPDATE SET role_id=excluded.role_id", (i.guild_id, level, role.id))
        await safe_send(i, embed=success("Reward saved."), ephemeral=True)

    @group.command(name="remove_reward")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_reward(self, i: discord.Interaction, level: int):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.bot.db.execute("DELETE FROM level_rewards WHERE guild_id=? AND level=?", (i.guild_id, level))
        await safe_send(i, embed=success("Reward removed."), ephemeral=True)

    @group.command(name="rewards")
    async def rewards(self, i: discord.Interaction):
        if not await safe_defer(i, ephemeral=False):
            return
        rows = await self.bot.db.fetchall("SELECT level,role_id FROM level_rewards WHERE guild_id=? ORDER BY level", (i.guild_id,))
        await safe_send(i, embed=make_embed("Level Rewards", "\n".join(f'L{r["level"]}: <@&{r["role_id"]}>' for r in rows) or "No rewards.", "leveling"), ephemeral=False)

    @group.command(name="disable")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self, i: discord.Interaction):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.bot.db.execute("INSERT INTO guild_config(guild_id,leveling_enabled) VALUES (?,0) ON CONFLICT(guild_id) DO UPDATE SET leveling_enabled=0", (i.guild_id,))
        await safe_send(i, embed=success("Leveling disabled."), ephemeral=True)

    @group.command(name="enable")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, i: discord.Interaction):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.bot.db.execute("INSERT INTO guild_config(guild_id,leveling_enabled) VALUES (?,1) ON CONFLICT(guild_id) DO UPDATE SET leveling_enabled=1", (i.guild_id,))
        await safe_send(i, embed=success("Leveling enabled."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
