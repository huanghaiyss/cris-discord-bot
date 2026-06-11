import random, discord
from discord import app_commands
from discord.ext import commands
from core.constants import MESSAGE_XP_MIN, MESSAGE_XP_MAX
from core.embeds import make_embed, success
from services.leveling_service import LevelingService, xp_for_level
class Leveling(commands.Cog):
    def __init__(self, bot): self.bot=bot; self.svc=LevelingService(bot.db)
    group=app_commands.Group(name='level', description='XP and levels')
    @commands.Cog.listener()
    async def on_message(self,msg:discord.Message):
        if not msg.guild or msg.author.bot: return
        conf=await self.bot.db.fetchone('SELECT leveling_enabled, level_channel_id FROM guild_config WHERE guild_id=?',(msg.guild.id,))
        if conf and not int(conf['leveling_enabled']): return
        res=await self.svc.add_xp(msg.guild.id,msg.author.id,random.randint(MESSAGE_XP_MIN,MESSAGE_XP_MAX),cooldown=True)
        if res and res.leveled_up:
            ch=msg.guild.get_channel(conf['level_channel_id']) if conf and conf['level_channel_id'] else msg.channel
            await ch.send(embed=make_embed('Level up!',f'{msg.author.mention} reached level **{res.level}**.','leveling'))
            rows=await self.bot.db.fetchall('SELECT role_id FROM level_rewards WHERE guild_id=? AND level<=?',(msg.guild.id,res.level))
            for r in rows:
                role=msg.guild.get_role(r['role_id'])
                if role and isinstance(msg.author,discord.Member) and msg.guild.me.top_role>role: await msg.author.add_roles(role,reason='Level reward')
    @group.command(name='rank')
    async def rank(self,i,user:discord.Member|None=None):
        u=user or i.user; r=await self.svc.rank(i.guild_id,u.id); await i.response.send_message(embed=make_embed('Rank',f'{u.mention}\nLevel: **{r["level"]}**\nXP: **{r["xp"]}/{xp_for_level(int(r["level"])+1)}**','leveling'))
    @group.command(name='leaderboard')
    async def leaderboard(self,i): rows=await self.svc.leaderboard(i.guild_id); await i.response.send_message(embed=make_embed('Level Leaderboard','\n'.join(f'{n+1}. <@{r["user_id"]}> — L{r["level"]} ({r["xp"]} XP)' for n,r in enumerate(rows)) or 'No XP yet.','leveling'))
    @group.command(name='set_channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(self,i,channel:discord.TextChannel): await self.bot.db.execute('INSERT INTO guild_config(guild_id,level_channel_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET level_channel_id=excluded.level_channel_id',(i.guild_id,channel.id)); await i.response.send_message(embed=success(f'Level channel: {channel.mention}'),ephemeral=True)
    @group.command(name='set_reward')
    @app_commands.checks.has_permissions(administrator=True)
    async def set_reward(self,i,level:app_commands.Range[int,1,1000],role:discord.Role): await self.bot.db.execute('INSERT INTO level_rewards(guild_id,level,role_id) VALUES (?,?,?) ON CONFLICT(guild_id,level) DO UPDATE SET role_id=excluded.role_id',(i.guild_id,level,role.id)); await i.response.send_message(embed=success('Reward saved.'),ephemeral=True)
    @group.command(name='remove_reward')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_reward(self,i,level:int): await self.bot.db.execute('DELETE FROM level_rewards WHERE guild_id=? AND level=?',(i.guild_id,level)); await i.response.send_message(embed=success('Reward removed.'),ephemeral=True)
    @group.command(name='rewards')
    async def rewards(self,i): rows=await self.bot.db.fetchall('SELECT level,role_id FROM level_rewards WHERE guild_id=? ORDER BY level',(i.guild_id,)); await i.response.send_message(embed=make_embed('Level Rewards','\n'.join(f'L{r["level"]}: <@&{r["role_id"]}>' for r in rows) or 'No rewards.','leveling'))
    @group.command(name='disable')
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self,i): await self.bot.db.execute('INSERT INTO guild_config(guild_id,leveling_enabled) VALUES (?,0) ON CONFLICT(guild_id) DO UPDATE SET leveling_enabled=0',(i.guild_id,)); await i.response.send_message(embed=success('Leveling disabled.'),ephemeral=True)
    @group.command(name='enable')
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self,i): await self.bot.db.execute('INSERT INTO guild_config(guild_id,leveling_enabled) VALUES (?,1) ON CONFLICT(guild_id) DO UPDATE SET leveling_enabled=1',(i.guild_id,)); await i.response.send_message(embed=success('Leveling enabled.'),ephemeral=True)
async def setup(bot): await bot.add_cog(Leveling(bot))
