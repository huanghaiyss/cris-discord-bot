from __future__ import annotations
import logging
from pathlib import Path
import discord
from discord.ext import commands
from core.config import Config
from core.database import Database
from core.errors import handle_app_command_error
log=logging.getLogger(__name__)
class EverythingBot(commands.Bot):
    def __init__(self, config:Config):
        intents=discord.Intents.all()
        super().__init__(command_prefix=config.default_prefix, intents=intents)
        self.config=config; self.db=Database(config.database_path); self.owner_ids_config=config.owner_ids or set()
    async def setup_hook(self):
        await self.db.open(); await self.db.apply_migrations(Path('migrations'))
        await self._load_cogs(); await self._register_views(); self.tree.on_error=handle_app_command_error
        if self.config.dev_guild_id:
            guild=discord.Object(id=self.config.dev_guild_id); self.tree.copy_global_to(guild=guild); synced=await self.tree.sync(guild=guild); log.info('Synced %d guild commands to %s', len(synced), self.config.dev_guild_id)
        else:
            synced=await self.tree.sync(); log.info('Synced %d global commands', len(synced))
    async def _load_cogs(self):
        for path in sorted(Path('cogs').glob('*.py')):
            if path.name.startswith('_') or path.stem=='__init__': continue
            ext=f'cogs.{path.stem}'
            try: await self.load_extension(ext); log.info('Loaded cog %s', ext)
            except Exception: log.exception('Failed loading cog %s', ext)
    async def _register_views(self):
        from views.tickets import TicketPanelView
        from views.suggestions import SuggestionVoteView
        from views.roleshop import RoleShopView
        self.add_view(TicketPanelView(self)); self.add_view(SuggestionVoteView(self)); self.add_view(RoleShopView(self)); log.info('Persistent views registered')
    async def close(self):
        log.info('Bot shutting down'); await self.db.close(); await super().close()
    async def on_ready(self): log.info('Logged in as %s (%s)', self.user, self.user.id if self.user else '?')
