from datetime import timedelta
import discord
from discord import app_commands
from discord.ext import commands
from core.checks import can_moderate, bot_can_act
from core.embeds import make_embed, success, error
from services.moderation_service import ModerationService
class Moderation(commands.Cog):
    def __init__(self, bot): self.bot=bot; self.svc=ModerationService(bot.db)
    group=app_commands.Group(name='mod', description='Moderation tools')
    async def _case(self,i,user,action,reason): cid,num=await self.svc.create_case(i.guild_id,user.id,i.user.id,action,reason); return cid,num
    async def _check(self,i,target):
        ok,msg=can_moderate(i.user,target,i.guild); ok2,msg2=bot_can_act(i.guild.me,target); return (ok and ok2, msg or msg2)
    @group.command(name='warn')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self,i,user:discord.Member,reason:str): cid,num=await self._case(i,user,'warn',reason); await self.svc.add_warning(i.guild_id,user.id,i.user.id,reason,cid); await i.response.send_message(embed=success(f'Warned {user.mention}. Case #{num}'),ephemeral=True)
    @group.command(name='warnings')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self,i,user:discord.Member): rows=await self.svc.warnings(i.guild_id,user.id); await i.response.send_message(embed=make_embed('Warnings','\n'.join(f'#{r["id"]}: {r["reason"]}' for r in rows) or 'No active warnings.','moderation'),ephemeral=True)
    @group.command(name='clear_warnings')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clear_warnings(self,i,user:discord.Member): await self.svc.clear_warnings(i.guild_id,user.id); await i.response.send_message(embed=success('Warnings cleared.'),ephemeral=True)
    @group.command(name='timeout')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self,i,user:discord.Member,duration_minutes:app_commands.Range[int,1,40320],reason:str='No reason provided'):
        ok,msg=await self._check(i,user)
        if not ok: return await i.response.send_message(embed=error(msg),ephemeral=True)
        await user.timeout(timedelta(minutes=duration_minutes),reason=reason); cid,num=await self._case(i,user,'timeout',reason); await i.response.send_message(embed=success(f'Timed out {user.mention}. Case #{num}'),ephemeral=True)
    @group.command(name='remove_timeout')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def remove_timeout(self,i,user:discord.Member,reason:str='No reason provided'): await user.timeout(None,reason=reason); cid,num=await self._case(i,user,'remove_timeout',reason); await i.response.send_message(embed=success(f'Removed timeout. Case #{num}'),ephemeral=True)
    @group.command(name='kick')
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self,i,user:discord.Member,reason:str='No reason provided'):
        ok,msg=await self._check(i,user)
        if not ok: return await i.response.send_message(embed=error(msg),ephemeral=True)
        await user.kick(reason=reason); cid,num=await self._case(i,user,'kick',reason); await i.response.send_message(embed=success(f'Kicked. Case #{num}'),ephemeral=True)
    @group.command(name='ban')
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self,i,user:discord.Member,delete_message_days:app_commands.Range[int,0,7]=0,reason:str='No reason provided'):
        ok,msg=await self._check(i,user)
        if not ok: return await i.response.send_message(embed=error(msg),ephemeral=True)
        await user.ban(delete_message_days=delete_message_days,reason=reason); cid,num=await self._case(i,user,'ban',reason); await i.response.send_message(embed=success(f'Banned. Case #{num}'),ephemeral=True)
    @group.command(name='unban')
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self,i,user_id:str,reason:str='No reason provided'):
        user=discord.Object(id=int(user_id)); await i.guild.unban(user,reason=reason); await self.svc.create_case(i.guild_id,int(user_id),i.user.id,'unban',reason); await i.response.send_message(embed=success('Unbanned.'),ephemeral=True)
    @group.command(name='case')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def case(self,i,case_id:int): row=await self.bot.db.fetchone('SELECT * FROM moderation_cases WHERE guild_id=? AND case_number=?',(i.guild_id,case_id)); await i.response.send_message(embed=make_embed(f'Case #{case_id}', str(dict(row)) if row else 'Not found.','moderation'),ephemeral=True)
    @group.command(name='cases')
    @app_commands.checks.has_permissions(moderate_members=True)
    async def cases(self,i,user:discord.Member): rows=await self.svc.cases_for(i.guild_id,user.id); await i.response.send_message(embed=make_embed('Cases','\n'.join(f'#{r["case_number"]}: {r["action"]} — {r["reason"]}' for r in rows) or 'No cases.','moderation'),ephemeral=True)
    @group.command(name='set_modlog')
    @app_commands.checks.has_permissions(administrator=True)
    async def set_modlog(self,i,channel:discord.TextChannel): await self.bot.db.execute('INSERT INTO guild_config(guild_id,mod_log_channel_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET mod_log_channel_id=excluded.mod_log_channel_id',(i.guild_id,channel.id)); await i.response.send_message(embed=success('Mod log saved.'),ephemeral=True)
async def setup(bot): await bot.add_cog(Moderation(bot))
