from __future__ import annotations
import time
from dataclasses import dataclass
from core.constants import XP_COOLDOWN_SECONDS
from core.database import Database

def level_for_xp(xp:int)->int:
    if xp<=0: return 0
    level=0
    while xp >= xp_for_level(level+1): level += 1
    return level

def xp_for_level(level:int)->int: return 100 * level * level
@dataclass(frozen=True)
class XPResult: xp:int; level:int; old_level:int; leveled_up:bool
class LevelingService:
    def __init__(self, db:Database): self.db=db
    async def ensure_user(self,guild_id:int,user_id:int): await self.db.execute('INSERT OR IGNORE INTO leveling_users(guild_id,user_id,xp,level,last_xp_at) VALUES (?,?,0,0,0)',(guild_id,user_id))
    async def add_xp(self,guild_id:int,user_id:int,amount:int,cooldown:bool=True)->XPResult|None:
        if amount<=0: raise ValueError('XP amount must be positive')
        await self.ensure_user(guild_id,user_id); row=await self.db.fetchone('SELECT xp,level,last_xp_at FROM leveling_users WHERE guild_id=? AND user_id=?',(guild_id,user_id)); now=time.time()
        if cooldown and now-float(row['last_xp_at'])<XP_COOLDOWN_SECONDS: return None
        xp=int(row['xp'])+amount; old=int(row['level']); new=level_for_xp(xp)
        await self.db.execute('UPDATE leveling_users SET xp=?, level=?, last_xp_at=? WHERE guild_id=? AND user_id=?',(xp,new,now,guild_id,user_id))
        return XPResult(xp,new,old,new>old)
    async def rank(self,guild_id:int,user_id:int): await self.ensure_user(guild_id,user_id); return await self.db.fetchone('SELECT * FROM leveling_users WHERE guild_id=? AND user_id=?',(guild_id,user_id))
    async def leaderboard(self,guild_id:int,limit:int=10): return await self.db.fetchall('SELECT user_id,xp,level FROM leveling_users WHERE guild_id=? ORDER BY xp DESC LIMIT ?',(guild_id,limit))
