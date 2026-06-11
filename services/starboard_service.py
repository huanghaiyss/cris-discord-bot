from core.database import Database
class StarboardService:
    def __init__(self, db:Database): self.db=db
    async def config(self,guild_id:int): await self.db.execute('INSERT OR IGNORE INTO starboard_config(guild_id) VALUES (?)',(guild_id,)); return await self.db.fetchone('SELECT * FROM starboard_config WHERE guild_id=?',(guild_id,))
    async def set_config(self,guild_id:int,channel_id:int|None,threshold:int=3,enabled:int=1): await self.config(guild_id); await self.db.execute('UPDATE starboard_config SET enabled=?, channel_id=?, threshold=? WHERE guild_id=?',(enabled,channel_id,threshold,guild_id))
    async def get_message(self,guild_id:int,msg_id:int): return await self.db.fetchone('SELECT * FROM starboard_messages WHERE guild_id=? AND source_message_id=?',(guild_id,msg_id))
    async def upsert_message(self,guild_id:int,src:int,star_id:int|None,channel_id:int,author_id:int,count:int): await self.db.execute('INSERT INTO starboard_messages(guild_id,source_message_id,starboard_message_id,channel_id,author_id,star_count) VALUES (?,?,?,?,?,?) ON CONFLICT(guild_id,source_message_id) DO UPDATE SET starboard_message_id=excluded.starboard_message_id, star_count=excluded.star_count',(guild_id,src,star_id,channel_id,author_id,count))
