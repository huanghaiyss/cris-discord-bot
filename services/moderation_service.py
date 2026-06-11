from __future__ import annotations
from core.database import Database
class ModerationService:
    def __init__(self, db:Database): self.db=db
    async def create_case(self,guild_id:int,user_id:int,moderator_id:int,action:str,reason:str|None):
        row=await self.db.fetchone('SELECT COALESCE(MAX(case_number),0)+1 AS n FROM moderation_cases WHERE guild_id=?',(guild_id,)); n=int(row['n'])
        cur=await self.db.execute('INSERT INTO moderation_cases(guild_id,case_number,user_id,moderator_id,action,reason) VALUES (?,?,?,?,?,?)',(guild_id,n,user_id,moderator_id,action,reason))
        return cur.lastrowid, n
    async def add_warning(self,guild_id:int,user_id:int,moderator_id:int,reason:str,case_id:int|None): await self.db.execute('INSERT INTO warnings(guild_id,user_id,moderator_id,reason,case_id) VALUES (?,?,?,?,?)',(guild_id,user_id,moderator_id,reason,case_id))
    async def warnings(self,guild_id:int,user_id:int): return await self.db.fetchall('SELECT * FROM warnings WHERE guild_id=? AND user_id=? AND active=1 ORDER BY created_at DESC',(guild_id,user_id))
    async def clear_warnings(self,guild_id:int,user_id:int): await self.db.execute('UPDATE warnings SET active=0 WHERE guild_id=? AND user_id=?',(guild_id,user_id))
    async def cases_for(self,guild_id:int,user_id:int): return await self.db.fetchall('SELECT * FROM moderation_cases WHERE guild_id=? AND user_id=? ORDER BY case_number DESC LIMIT 20',(guild_id,user_id))
