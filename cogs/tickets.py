import discord
from discord import app_commands
from discord.ext import commands
from core.embeds import make_embed, success
from services.ticket_service import TicketService
from views.tickets import TicketPanelView
class Tickets(commands.Cog):
    def __init__(self,bot): self.bot=bot; self.svc=TicketService(bot.db)
    group=app_commands.Group(name='ticket', description='Ticket system')
    @group.command(name='panel')
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self,i,channel:discord.TextChannel,title:str='Support Tickets',description:str='Click to open a private ticket.'):
        await channel.send(embed=make_embed(title,description,'tickets'),view=TicketPanelView(self.bot)); await i.response.send_message(embed=success('Ticket panel sent.'),ephemeral=True)
    @group.command(name='close')
    async def close(self,i,reason:str='No reason provided'):
        row=await self.svc.by_channel(i.guild_id,i.channel_id)
        if not row: return await i.response.send_message('No open ticket here.',ephemeral=True)
        await self.svc.close(int(row['id']),i.user.id,reason); await i.response.send_message(embed=success('Ticket closed.'),ephemeral=True)
    @group.command(name='add_user')
    async def add_user(self,i,user:discord.Member): await i.channel.set_permissions(user,view_channel=True,send_messages=True,read_message_history=True); await i.response.send_message(embed=success('User added.'),ephemeral=True)
    @group.command(name='remove_user')
    async def remove_user(self,i,user:discord.Member): await i.channel.set_permissions(user,overwrite=None); await i.response.send_message(embed=success('User removed.'),ephemeral=True)
    @group.command(name='config_category')
    @app_commands.checks.has_permissions(administrator=True)
    async def config_category(self,i,category:discord.CategoryChannel): await self.bot.db.execute('INSERT INTO guild_config(guild_id,ticket_category_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET ticket_category_id=excluded.ticket_category_id',(i.guild_id,category.id)); await i.response.send_message(embed=success('Ticket category saved.'),ephemeral=True)
    @group.command(name='config_log_channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def config_log_channel(self,i,channel:discord.TextChannel): await self.bot.db.execute('INSERT INTO guild_config(guild_id,ticket_log_channel_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET ticket_log_channel_id=excluded.ticket_log_channel_id',(i.guild_id,channel.id)); await i.response.send_message(embed=success('Ticket log channel saved.'),ephemeral=True)
async def setup(bot): await bot.add_cog(Tickets(bot))
