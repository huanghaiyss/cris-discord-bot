import platform, discord
from discord import app_commands
from discord.ext import commands
from core.embeds import make_embed
class Utility(commands.Cog):
    def __init__(self,bot): self.bot=bot
    group=app_commands.Group(name='utility', description='Server utilities')
    @group.command(name='ping')
    async def ping(self,i): await i.response.send_message(embed=make_embed('Pong',f'{self.bot.latency*1000:.0f} ms','info'))
    @group.command(name='userinfo')
    async def userinfo(self,i,user:discord.Member|None=None): u=user or i.user; await i.response.send_message(embed=make_embed('User Info',f'{u.mention}\nID: `{u.id}`\nJoined: {getattr(u,"joined_at",None)}','info'))
    @group.command(name='serverinfo')
    async def serverinfo(self,i): g=i.guild; await i.response.send_message(embed=make_embed('Server Info',f'{g.name}\nMembers: {g.member_count}\nID: `{g.id}`','info'))
    @group.command(name='avatar')
    async def avatar(self,i,user:discord.User|None=None): u=user or i.user; e=make_embed('Avatar',u.mention,'info'); e.set_image(url=u.display_avatar.url); await i.response.send_message(embed=e)
    @group.command(name='botinfo')
    async def botinfo(self,i): await i.response.send_message(embed=make_embed('Bot Info',f'discord.py {discord.__version__}\nPython {platform.python_version()}\nGuilds: {len(self.bot.guilds)}','info'))
    @group.command(name='channelinfo')
    async def channelinfo(self,i,channel:discord.TextChannel|None=None): c=channel or i.channel; await i.response.send_message(embed=make_embed('Channel Info',f'{c.mention}\nID: `{c.id}`\nTopic: {getattr(c,"topic",None)}','info'))
    @group.command(name='roleinfo')
    async def roleinfo(self,i,role:discord.Role): await i.response.send_message(embed=make_embed('Role Info',f'{role.mention}\nID: `{role.id}`\nMembers: {len(role.members)}','info'))
    @group.command(name='invite_info')
    async def invite_info(self,i,invite:str):
        try: inv=await self.bot.fetch_invite(invite); txt=f'Guild: {inv.guild}\nChannel: {inv.channel}\nUses: {inv.uses}'
        except discord.HTTPException: txt='Invite not found or not accessible.'
        await i.response.send_message(embed=make_embed('Invite Info',txt,'info'),ephemeral=True)
    @group.command(name='poll')
    async def poll(self,i,question:str,options:str):
        opts=[o.strip() for o in options.split('|') if o.strip()][:10]; emojis=['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']; e=make_embed('Poll',question+'\n\n'+'\n'.join(f'{emojis[n]} {o}' for n,o in enumerate(opts)),'info'); await i.response.send_message(embed=e); m=await i.original_response(); [await m.add_reaction(emojis[n]) for n in range(len(opts))]
async def setup(bot): await bot.add_cog(Utility(bot))
