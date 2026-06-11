import discord
from discord import app_commands
from discord.ext import commands

from core.embeds import error, make_embed, success
from core.interactions import safe_defer, safe_send
from services.roleshop_service import RoleShopService


class RoleShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.svc = RoleShopService(bot.db)

    group = app_commands.Group(name="roleshop", description="Buy roles with fake coins")

    @group.command(name="list")
    async def list(self, i: discord.Interaction):
        if not await safe_defer(i, ephemeral=False):
            return
        rows = await self.svc.list(i.guild_id)
        await safe_send(i, embed=make_embed("Role Shop", "\n".join(f'<@&{r["role_id"]}> — {r["price"]}' for r in rows) or "No roles for sale.", "economy"), ephemeral=False)

    @group.command(name="buy")
    async def buy(self, i: discord.Interaction, role: discord.Role):
        if not await safe_defer(i, ephemeral=True):
            return
        if role in i.user.roles:
            await safe_send(i, embed=error("You already have that role."), ephemeral=True)
            return
        if role.managed or role >= i.guild.me.top_role:
            await safe_send(i, embed=error("I cannot assign that role."), ephemeral=True)
            return
        try:
            price = await self.svc.purchase(i.guild_id, i.user.id, role.id)
            await i.user.add_roles(role, reason="Role shop purchase")
            await safe_send(i, embed=success(f"Bought {role.mention} for {price} coins."), ephemeral=True)
        except Exception as exc:
            await safe_send(i, embed=error(str(exc)), ephemeral=True)

    @group.command(name="add")
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, i: discord.Interaction, role: discord.Role, price: app_commands.Range[int, 1, 100000000]):
        if not await safe_defer(i, ephemeral=True):
            return
        if role.managed or role >= i.guild.me.top_role:
            await safe_send(i, embed=error("Bot role must be above target and role cannot be managed."), ephemeral=True)
            return
        await self.svc.add(i.guild_id, role.id, price)
        await safe_send(i, embed=success("Role shop item saved."), ephemeral=True)

    @group.command(name="remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, i: discord.Interaction, role: discord.Role):
        if not await safe_defer(i, ephemeral=True):
            return
        await self.svc.remove(i.guild_id, role.id)
        await safe_send(i, embed=success("Removed."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(RoleShop(bot))
