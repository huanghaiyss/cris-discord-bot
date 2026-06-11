from core.database import Database
class SuggestionService:
    def __init__(self, db:Database): self.db=db
    async def create(self,guild_id:int,user_id:int,text:str,channel_id:int|None=None,message_id:int|None=None):
        cur=await self.db.execute('INSERT INTO suggestions(guild_id,user_id,text,channel_id,message_id) VALUES (?,?,?,?,?)',(guild_id,user_id,text,channel_id,message_id)); return cur.lastrowid
    async def set_message(self,sid:int,channel_id:int,message_id:int): await self.db.execute('UPDATE suggestions SET channel_id=?, message_id=? WHERE id=?',(channel_id,message_id,sid))
    async def vote(self,sid:int,user_id:int,vote:int): await self.db.execute('INSERT INTO suggestion_votes(suggestion_id,user_id,vote) VALUES (?,?,?) ON CONFLICT(suggestion_id,user_id) DO UPDATE SET vote=excluded.vote',(sid,user_id,vote))
    async def counts(self,sid:int): return await self.db.fetchone('SELECT COALESCE(SUM(vote=1),0) AS up, COALESCE(SUM(vote=-1),0) AS down FROM suggestion_votes WHERE suggestion_id=?',(sid,))
