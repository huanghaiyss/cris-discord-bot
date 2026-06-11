import discord
from discord import app_commands
from discord.ext import commands
from core.embeds import make_embed, success, error
from services.roleshop_service import RoleShopService
class RoleShop(commands.Cog):
    def __init__(self,bot): self.bot=bot; self.svc=RoleShopService(bot.db)
    group=app_commands.Group(name='roleshop', description='Buy roles with fake coins')
    @group.command(name='list')
    async def list(self,i): rows=await self.svc.list(i.guild_id); await i.response.send_message(embed=make_embed('Role Shop','\n'.join(f'<@&{r["role_id"]}> — {r["price"]}' for r in rows) or 'No roles for sale.','economy'))
    @group.command(name='buy')
    async def buy(self,i,role:discord.Role):
        if role in i.user.roles: return await i.response.send_message(embed=error('You already have that role.'),ephemeral=True)
        if role.managed or role>=i.guild.me.top_role: return await i.response.send_message(embed=error('I cannot assign that role.'),ephemeral=True)
        try: price=await self.svc.purchase(i.guild_id,i.user.id,role.id); await i.user.add_roles(role,reason='Role shop purchase'); await i.response.send_message(embed=success(f'Bought {role.mention} for {price} coins.'),ephemeral=True)
        except Exception as e: await i.response.send_message(embed=error(str(e)),ephemeral=True)
    @group.command(name='add')
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self,i,role:discord.Role,price:app_commands.Range[int,1,100000000]):
        if role.managed or role>=i.guild.me.top_role: return await i.response.send_message(embed=error('Bot role must be above target and role cannot be managed.'),ephemeral=True)
        await self.svc.add(i.guild_id,role.id,price); await i.response.send_message(embed=success('Role shop item saved.'),ephemeral=True)
    @group.command(name='remove')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self,i,role:discord.Role): await self.svc.remove(i.guild_id,role.id); await i.response.send_message(embed=success('Removed.'),ephemeral=True)
async def setup(bot): await bot.add_cog(RoleShop(bot))
