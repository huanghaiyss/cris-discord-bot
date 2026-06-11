import discord
from discord import app_commands
from discord.ext import commands
from core.embeds import make_embed, success
from services.suggestion_service import SuggestionService
from views.suggestions import SuggestionVoteView
class Suggestions(commands.Cog):
    def __init__(self,bot): self.bot=bot; self.svc=SuggestionService(bot.db)
    group=app_commands.Group(name='suggest', description='Suggestions')
    @group.command(name='submit')
    async def submit(self,i,text:str):
        conf=await self.bot.db.fetchone('SELECT suggestion_channel_id FROM guild_config WHERE guild_id=?',(i.guild_id,)); ch=i.guild.get_channel(conf['suggestion_channel_id']) if conf and conf['suggestion_channel_id'] else i.channel
        sid=await self.svc.create(i.guild_id,i.user.id,text,ch.id,None); msg=await ch.send(embed=make_embed(f'Suggestion #{sid}',f'{text}\n\nBy {i.user.mention}\nStatus: pending','suggestions'),view=SuggestionVoteView(self.bot)); await self.svc.set_message(sid,ch.id,msg.id); await i.response.send_message(embed=success(f'Suggestion submitted as #{sid}.'),ephemeral=True)
    @group.command(name='channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def channel(self,i,channel:discord.TextChannel): await self.bot.db.execute('INSERT INTO guild_config(guild_id,suggestion_channel_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET suggestion_channel_id=excluded.suggestion_channel_id',(i.guild_id,channel.id)); await i.response.send_message(embed=success('Suggestion channel saved.'),ephemeral=True)
    @group.command(name='status')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def status(self,i,suggestion_id:int,status:str,reason:str=''):
        allowed={'pending','accepted','rejected','implemented'}
        if status not in allowed: return await i.response.send_message(f'Status must be one of {allowed}',ephemeral=True)
        await self.bot.db.execute('UPDATE suggestions SET status=?, reason=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND guild_id=?',(status,reason,suggestion_id,i.guild_id)); await i.response.send_message(embed=success('Suggestion updated.'),ephemeral=True)
async def setup(bot): await bot.add_cog(Suggestions(bot))
