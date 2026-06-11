import discord
from services.ticket_service import TicketService
class TicketPanelView(discord.ui.View):
    def __init__(self, bot): super().__init__(timeout=None); self.bot=bot
    @discord.ui.button(label='Open Ticket', emoji='🎫', style=discord.ButtonStyle.primary, custom_id='ticket:open')
    async def open_ticket(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not interaction.guild or not isinstance(interaction.user, discord.Member): return
        svc=TicketService(self.bot.db); existing=await svc.active_for_user(interaction.guild.id, interaction.user.id)
        if existing: return await interaction.response.send_message(f'You already have an open ticket: <#{existing["channel_id"]}>', ephemeral=True)
        conf=await self.bot.db.fetchone('SELECT ticket_category_id FROM guild_config WHERE guild_id=?',(interaction.guild.id,)); category=interaction.guild.get_channel(conf['ticket_category_id']) if conf and conf['ticket_category_id'] else None
        overwrites={interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)}
        channel=await interaction.guild.create_text_channel(f'ticket-{interaction.user.name}'.lower()[:90], category=category if isinstance(category, discord.CategoryChannel) else None, overwrites=overwrites, reason='Ticket opened')
        tid=await svc.open_ticket(interaction.guild.id, interaction.user.id, channel.id)
        await channel.send(f'{interaction.user.mention} ticket #{tid}', view=TicketCloseView(self.bot))
        await interaction.response.send_message(f'Opened {channel.mention}', ephemeral=True)
class TicketCloseView(discord.ui.View):
    def __init__(self, bot): super().__init__(timeout=None); self.bot=bot
    @discord.ui.button(label='Close Ticket', style=discord.ButtonStyle.danger, custom_id='ticket:close')
    async def close_ticket(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not interaction.guild or not interaction.channel: return
        svc=TicketService(self.bot.db); row=await svc.by_channel(interaction.guild.id, interaction.channel.id)
        if not row: return await interaction.response.send_message('No open ticket for this channel.', ephemeral=True)
        await svc.close(int(row['id']), interaction.user.id, 'Closed with button')
        await interaction.response.send_message('Closing ticket...', ephemeral=True)
        await interaction.channel.edit(name=f'closed-{interaction.channel.name[:80]}')
