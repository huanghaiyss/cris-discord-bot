import random
import discord
from discord import app_commands
from discord.ext import commands
from core.constants import CURRENCY_NAME
from core.embeds import make_embed, success, error
from services.economy_service import EconomyService, BalanceChange, EconomyError
class Economy(commands.Cog):
    def __init__(self, bot): self.bot=bot; self.svc=EconomyService(bot.db)
    group=app_commands.Group(name='economy', description='Fake in-server currency')
    @group.command(name='balance')
    async def balance(self,i:discord.Interaction,user:discord.Member|None=None):
        u=user or i.user; bal=await self.svc.balance(i.guild_id,u.id); await i.response.send_message(embed=make_embed('Balance',f'{u.mention}: **{bal} {CURRENCY_NAME}**','economy'))
    @group.command(name='daily')
    @app_commands.checks.cooldown(1,86400,key=lambda i:(i.guild_id,i.user.id))
    async def daily(self,i): bal=await self.svc.daily(i.guild_id,i.user.id); await i.response.send_message(embed=success(f'Claimed daily. Balance: {bal} {CURRENCY_NAME}'))
    @group.command(name='work')
    @app_commands.checks.cooldown(1,3600,key=lambda i:(i.guild_id,i.user.id))
    async def work(self,i): r=await self.svc.work(i.guild_id,i.user.id); await i.response.send_message(embed=make_embed('Work',f'You earned **{r} {CURRENCY_NAME}**.','economy'))
    @group.command(name='pay')
    async def pay(self,i,user:discord.Member,amount:app_commands.Range[int,1,1000000]):
        try: await self.svc.transfer(i.guild_id,i.user.id,user.id,amount); await i.response.send_message(embed=success(f'Paid {user.mention} {amount} {CURRENCY_NAME}.'))
        except EconomyError as e: await i.response.send_message(embed=error(str(e)), ephemeral=True)
    @group.command(name='slots')
    @app_commands.checks.cooldown(1,10,key=lambda i:(i.guild_id,i.user.id))
    async def slots(self,i,amount:app_commands.Range[int,1,100000]):
        icons=['🍒','🍋','🔔','💎','7️⃣']; roll=[random.choice(icons) for _ in range(3)]; mult=5 if len(set(roll))==1 else 2 if len(set(roll))==2 else 0
        try:
            await self.svc.change_balance(BalanceChange(i.guild_id,i.user.id,-amount,'slots_bet'))
            win=amount*mult
            if win: await self.svc.change_balance(BalanceChange(i.guild_id,i.user.id,win,'slots_win'))
            await i.response.send_message(embed=make_embed('Slots',' '.join(roll)+f'\nNet: {win-amount} {CURRENCY_NAME}','economy'))
        except EconomyError as e: await i.response.send_message(embed=error(str(e)),ephemeral=True)
    @group.command(name='blackjack')
    @app_commands.checks.cooldown(1,15,key=lambda i:(i.guild_id,i.user.id))
    async def blackjack(self,i,amount:app_commands.Range[int,1,100000]):
        try: await self.svc.change_balance(BalanceChange(i.guild_id,i.user.id,-amount,'blackjack_bet'))
        except EconomyError as e: return await i.response.send_message(embed=error(str(e)),ephemeral=True)
        player=random.randint(16,23); dealer=random.randint(17,23); win=(player<=21 and (dealer>21 or player>dealer)); prize=amount*2 if win else 0
        if prize: await self.svc.change_balance(BalanceChange(i.guild_id,i.user.id,prize,'blackjack_win'))
        await i.response.send_message(embed=make_embed('Blackjack',f'You: {player}\nDealer: {dealer}\n{"Won" if win else "Lost"}: {prize-amount} {CURRENCY_NAME}','economy'))
    @group.command(name='inventory')
    async def inventory(self,i):
        rows=await self.bot.db.fetchall('SELECT item_name,quantity FROM user_inventory WHERE guild_id=? AND user_id=?',(i.guild_id,i.user.id)); txt='\n'.join(f'{r["item_name"]} x{r["quantity"]}' for r in rows) or 'Inventory is empty.'; await i.response.send_message(embed=make_embed('Inventory',txt,'economy'),ephemeral=True)
    @group.command(name='leaderboard')
    async def leaderboard(self,i):
        rows=await self.svc.leaderboard(i.guild_id); txt='\n'.join(f'{n+1}. <@{r["user_id"]}> — {r["balance"]}' for n,r in enumerate(rows)) or 'No balances yet.'; await i.response.send_message(embed=make_embed('Economy Leaderboard',txt,'economy'))
    @group.command(name='shop')
    async def shop(self,i):
        rows=await self.bot.db.fetchall('SELECT name,price,description FROM shop_items WHERE guild_id=? ORDER BY price',(i.guild_id,)); txt='\n'.join(f'**{r["name"]}** — {r["price"]}: {r["description"] or ""}' for r in rows) or 'Shop is empty.'; await i.response.send_message(embed=make_embed('Shop',txt,'economy'))
    @group.command(name='buy')
    async def buy(self,i,item:str): await i.response.send_message(embed=error('Item shop purchases are configured by server-specific extensions; use /roleshop for role purchases.'),ephemeral=True)
    @group.command(name='give')
    @app_commands.checks.has_permissions(administrator=True)
    async def give(self,i,user:discord.Member,amount:app_commands.Range[int,1,1000000]): bal=await self.svc.change_balance(BalanceChange(i.guild_id,user.id,amount,'admin_give',i.user.id)); await i.response.send_message(embed=success(f'{user.mention} balance: {bal}'),ephemeral=True)
    @group.command(name='take')
    @app_commands.checks.has_permissions(administrator=True)
    async def take(self,i,user:discord.Member,amount:app_commands.Range[int,1,1000000]):
        try: bal=await self.svc.change_balance(BalanceChange(i.guild_id,user.id,-amount,'admin_take',i.user.id)); await i.response.send_message(embed=success(f'{user.mention} balance: {bal}'),ephemeral=True)
        except EconomyError as e: await i.response.send_message(embed=error(str(e)),ephemeral=True)
async def setup(bot): await bot.add_cog(Economy(bot))
