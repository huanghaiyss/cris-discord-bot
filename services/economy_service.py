from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import random
from core.constants import DAILY_REWARD, MAX_BALANCE, WORK_MAX_REWARD, WORK_MIN_REWARD
from core.database import Database

class EconomyError(ValueError): pass
@dataclass(frozen=True)
class BalanceChange: guild_id:int; user_id:int; amount:int; reason:str; related_user_id:int|None=None

class EconomyService:
    def __init__(self, db: Database): self.db=db
    async def ensure_user(self,guild_id:int,user_id:int)->None:
        await self.db.execute('INSERT OR IGNORE INTO economy_users(guild_id,user_id,balance) VALUES (?,?,0)',(guild_id,user_id))
    async def balance(self,guild_id:int,user_id:int)->int:
        await self.ensure_user(guild_id,user_id); row=await self.db.fetchone('SELECT balance FROM economy_users WHERE guild_id=? AND user_id=?',(guild_id,user_id)); return int(row['balance'])
    async def change_balance(self, c:BalanceChange)->int:
        if c.amount==0: raise EconomyError('Amount must not be zero.')
        await self.ensure_user(c.guild_id,c.user_id)
        bal=await self.balance(c.guild_id,c.user_id); new=bal+c.amount
        if new<0: raise EconomyError('Insufficient funds.')
        if new>MAX_BALANCE: raise EconomyError('Balance limit exceeded.')
        async with self.db.transaction() as conn:
            await conn.execute('UPDATE economy_users SET balance=?, updated_at=CURRENT_TIMESTAMP WHERE guild_id=? AND user_id=?',(new,c.guild_id,c.user_id))
            await conn.execute('INSERT INTO economy_transactions(guild_id,user_id,amount,reason,related_user_id) VALUES (?,?,?,?,?)',(c.guild_id,c.user_id,c.amount,c.reason,c.related_user_id))
        return new
    async def transfer(self,guild_id:int,from_user:int,to_user:int,amount:int,reason='pay')->tuple[int,int]:
        if amount<=0: raise EconomyError('Amount must be positive.')
        if from_user==to_user: raise EconomyError('Cannot pay yourself.')
        async with self.db.transaction() as conn:
            await conn.execute('INSERT OR IGNORE INTO economy_users(guild_id,user_id,balance) VALUES (?,?,0)',(guild_id,from_user)); await conn.execute('INSERT OR IGNORE INTO economy_users(guild_id,user_id,balance) VALUES (?,?,0)',(guild_id,to_user))
            r=await (await conn.execute('SELECT balance FROM economy_users WHERE guild_id=? AND user_id=?',(guild_id,from_user))).fetchone(); bal=int(r['balance'])
            if bal<amount: raise EconomyError('Insufficient funds.')
            await conn.execute('UPDATE economy_users SET balance=balance-?, updated_at=CURRENT_TIMESTAMP WHERE guild_id=? AND user_id=?',(amount,guild_id,from_user))
            await conn.execute('UPDATE economy_users SET balance=balance+?, updated_at=CURRENT_TIMESTAMP WHERE guild_id=? AND user_id=?',(amount,guild_id,to_user))
            await conn.execute('INSERT INTO economy_transactions(guild_id,user_id,amount,reason,related_user_id) VALUES (?,?,?,?,?)',(guild_id,from_user,-amount,reason,to_user)); await conn.execute('INSERT INTO economy_transactions(guild_id,user_id,amount,reason,related_user_id) VALUES (?,?,?,?,?)',(guild_id,to_user,amount,reason,from_user))
        return await self.balance(guild_id,from_user), await self.balance(guild_id,to_user)
    async def daily(self,guild_id:int,user_id:int)->int: return await self.change_balance(BalanceChange(guild_id,user_id,DAILY_REWARD,'daily'))
    async def work(self,guild_id:int,user_id:int)->int:
        reward=random.randint(WORK_MIN_REWARD,WORK_MAX_REWARD); await self.change_balance(BalanceChange(guild_id,user_id,reward,'work')); return reward
    async def leaderboard(self,guild_id:int,limit:int=10): return await self.db.fetchall('SELECT user_id,balance FROM economy_users WHERE guild_id=? ORDER BY balance DESC LIMIT ?',(guild_id,limit))
