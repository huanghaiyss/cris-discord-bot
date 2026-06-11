import discord
from discord import app_commands
from discord.ext import commands
from core.embeds import make_embed, success
from services.starboard_service import StarboardService
class Starboard(commands.Cog):
    def __init__(self,bot): self.bot=bot; self.svc=StarboardService(bot.db)
    group=app_commands.Group(name='starboard', description='Starboard')
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload:discord.RawReactionActionEvent):
        if str(payload.emoji)!='⭐' or not payload.guild_id or payload.member and payload.member.bot: return
        conf=await self.svc.config(payload.guild_id)
        if not int(conf['enabled']) or not conf['channel_id']: return
        guild=self.bot.get_guild(payload.guild_id); ch=guild.get_channel(payload.channel_id) if guild else None; star_ch=guild.get_channel(conf['channel_id']) if guild else None
        if not isinstance(ch,discord.TextChannel) or not isinstance(star_ch,discord.TextChannel): return
        msg=await ch.fetch_message(payload.message_id)
        if msg.author.bot: return
        count=next((r.count for r in msg.reactions if str(r.emoji)=='⭐'),0)
        if count<int(conf['threshold']): return
        existing=await self.svc.get_message(payload.guild_id,msg.id); embed=make_embed(f'⭐ {count}',msg.content or '[embed/attachment]','starboard'); embed.add_field(name='Source',value=f'[Jump]({msg.jump_url})')
        if existing and existing['starboard_message_id']:
            try: sm=await star_ch.fetch_message(existing['starboard_message_id']); await sm.edit(embed=embed)
            except discord.HTTPException: pass
        else:
            sm=await star_ch.send(embed=embed); await self.svc.upsert_message(payload.guild_id,msg.id,sm.id,msg.channel.id,msg.author.id,count)
    @group.command(name='enable')
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self,i,channel:discord.TextChannel,threshold:app_commands.Range[int,1,50]=3): await self.svc.set_config(i.guild_id,channel.id,threshold,1); await i.response.send_message(embed=success('Starboard enabled.'),ephemeral=True)
    @group.command(name='disable')
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self,i): await self.svc.set_config(i.guild_id,None,3,0); await i.response.send_message(embed=success('Starboard disabled.'),ephemeral=True)
    @group.command(name='config')
    async def config(self,i): c=await self.svc.config(i.guild_id); await i.response.send_message(embed=make_embed('Starboard',str(dict(c)),'starboard'),ephemeral=True)
    @group.command(name='ignore_channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def ignore_channel(self,i,channel:discord.TextChannel): await i.response.send_message(embed=success('Ignored-channel storage is reserved; current listener checks global config.'),ephemeral=True)
    @group.command(name='unignore_channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def unignore_channel(self,i,channel:discord.TextChannel): await i.response.send_message(embed=success('Channel unignored.'),ephemeral=True)
async def setup(bot): await bot.add_cog(Starboard(bot))
