import discord
from discord import app_commands
from discord.ext import commands

from core.embeds import make_embed, success
from core.interactions import safe_defer, safe_send
from services.ticket_service import TicketService
from views.tickets import TicketPanelView


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.svc = TicketService(bot.db)

    group = app_commands.Group(name="ticket", description="Ticket system")

    @group.command(name="panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, i: discord.Interaction, channel: discord.TextChannel, title: str = "Support Tickets", description: str = "Click to open a private ticket."):
        if not await safe_defer(i, ephemeral=True):
            return
        await channel.send(embed=make_embed(title, description, "tickets"), view=TicketPanelView(self.bot))
        await safe_send(i, embed=success("Ticket panel sent."), ephemeral=True)

    @group.command(name="close")
    async def close(self, i: discord.Interaction, reason: str = "No reason provided"):
        if not await safe_defer(i, ephemeral=True):
            return
        row = await self.svc.by_channel(i.guild_id, i.channel_id)
        if not row:
            await safe_send(i, "No open ticket here.", ephemeral=True)
            return
        await self.svc.close(int(row["id"]), i.user.id, reason)
        await safe_send(i, embed=success("Ticket closed."), ephemeral=True)

    @group.command(name="add_user")
    async def add_user(self, i: discord.Interaction, user: discord.Member):
        if not await safe_defer(i, ephemeral=True):
            return
        await i.channel.set_permissions(user, view_channel=True, send_messages=True, read_message_history=True)
        await safe_send(i, embed=success("User added."), ephemeral=True)

    @group.command(name="remove_user")
    async def remove_user(self, i: discord.Interaction, user: discord.Member):
        if not await safe_defer(i, ephemeral=True):
            return
        await i.channel.set_permissions(user, overwrite=None)
        await safe_send(i, embed=success("User removed."), ephemeral=True)

    @group.command(name="config_category")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_category(self, i: discord.Interaction, category: discord.CategoryChannel):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.bot.db.execute("INSERT INTO guild_config(guild_id,ticket_category_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET ticket_category_id=excluded.ticket_category_id", (i.guild_id, category.id))
        await safe_send(i, embed=success("Ticket category saved."), ephemeral=True)

    @group.command(name="config_log_channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_log_channel(self, i: discord.Interaction, channel: discord.TextChannel):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.bot.db.execute("INSERT INTO guild_config(guild_id,ticket_log_channel_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET ticket_log_channel_id=excluded.ticket_log_channel_id", (i.guild_id, channel.id))
        await safe_send(i, embed=success("Ticket log channel saved."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
