from __future__ import annotations
import re, time
from collections import defaultdict, deque
from core.database import Database
INVITE_RE=re.compile(r'(discord\.gg/|discord(?:app)?\.com/invite/)', re.I)
LINK_RE=re.compile(r'https?://[^\s]+', re.I)
class AutomodService:
    def __init__(self, db:Database): self.db=db; self.messages=defaultdict(lambda: deque(maxlen=10)); self.joins=defaultdict(lambda: deque(maxlen=20)); self.deleted_mentions={}
    async def config(self,guild_id:int):
        await self.db.execute('INSERT OR IGNORE INTO automod_config(guild_id) VALUES (?)',(guild_id,)); return await self.db.fetchone('SELECT * FROM automod_config WHERE guild_id=?',(guild_id,))
    async def set_flag(self,guild_id:int,key:str,value:int):
        if key not in {'enabled','invite_filter','link_filter','panic_mode'}: raise ValueError('bad key')
        await self.config(guild_id); await self.db.execute(f'UPDATE automod_config SET {key}=? WHERE guild_id=?',(int(value),guild_id))
    async def set_int(self,guild_id:int,key:str,value:int):
        if key not in {'spam_threshold','mention_threshold','log_channel_id'}: raise ValueError('bad key')
        await self.config(guild_id); await self.db.execute(f'UPDATE automod_config SET {key}=? WHERE guild_id=?',(value,guild_id))
    async def record_violation(self,guild_id:int,user_id:int,vtype:str,content:str|None,action:str): await self.db.execute('INSERT INTO automod_violations(guild_id,user_id,violation_type,content,action_taken) VALUES (?,?,?,?,?)',(guild_id,user_id,vtype,(content or '')[:500],action))
    def inspect_message(self,guild_id:int,user_id:int,content:str,mentions:int,conf)->str|None:
        now=time.time(); q=self.messages[(guild_id,user_id)]; q.append((now,content)); recent=[m for t,m in q if now-t<8]
        if len(recent)>=int(conf['spam_threshold']): return 'spam'
        if len(recent)>=3 and len(set(recent[-3:]))==1: return 'repeated_message'
        if mentions>=int(conf['mention_threshold']): return 'mention_spam'
        if int(conf['invite_filter']) and INVITE_RE.search(content): return 'invite_link'
        if int(conf['link_filter']) and LINK_RE.search(content): return 'link'
        return None
