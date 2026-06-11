from core.database import Database
from services.economy_service import EconomyService, BalanceChange
class RoleShopService:
    def __init__(self, db:Database): self.db=db; self.economy=EconomyService(db)
    async def add(self,guild_id:int,role_id:int,price:int): await self.db.execute('INSERT INTO role_shop_items(guild_id,role_id,price) VALUES (?,?,?) ON CONFLICT(guild_id,role_id) DO UPDATE SET price=excluded.price',(guild_id,role_id,price))
    async def remove(self,guild_id:int,role_id:int): await self.db.execute('DELETE FROM role_shop_items WHERE guild_id=? AND role_id=?',(guild_id,role_id))
    async def list(self,guild_id:int): return await self.db.fetchall('SELECT * FROM role_shop_items WHERE guild_id=? ORDER BY price',(guild_id,))
    async def item(self,guild_id:int,role_id:int): return await self.db.fetchone('SELECT * FROM role_shop_items WHERE guild_id=? AND role_id=?',(guild_id,role_id))
    async def purchase(self,guild_id:int,user_id:int,role_id:int):
        item=await self.item(guild_id,role_id)
        if not item: raise ValueError('Role is not for sale.')
        await self.economy.change_balance(BalanceChange(guild_id,user_id,-int(item['price']),f'role_shop:{role_id}'))
        return int(item['price'])
