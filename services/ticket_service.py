from core.database import Database
class TicketService:
    def __init__(self, db:Database): self.db=db
    async def open_ticket(self,guild_id:int,user_id:int,channel_id:int):
        cur=await self.db.execute('INSERT INTO tickets(guild_id,user_id,channel_id) VALUES (?,?,?)',(guild_id,user_id,channel_id)); return cur.lastrowid
    async def active_for_user(self,guild_id:int,user_id:int): return await self.db.fetchone("SELECT * FROM tickets WHERE guild_id=? AND user_id=? AND status='open'",(guild_id,user_id))
    async def by_channel(self,guild_id:int,channel_id:int): return await self.db.fetchone("SELECT * FROM tickets WHERE guild_id=? AND channel_id=? AND status='open'",(guild_id,channel_id))
    async def close(self,ticket_id:int,actor_id:int,reason:str): await self.db.execute("UPDATE tickets SET status='closed', closed_at=CURRENT_TIMESTAMP, closed_by=?, close_reason=? WHERE id=?",(actor_id,reason,ticket_id)); await self.db.execute('INSERT INTO ticket_logs(ticket_id,action,actor_id,note) VALUES (?,?,?,?)',(ticket_id,'closed',actor_id,reason))
