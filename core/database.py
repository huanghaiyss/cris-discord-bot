from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Iterable
import aiosqlite
log = logging.getLogger(__name__)

class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.conn: aiosqlite.Connection | None = None

    async def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute('PRAGMA journal_mode=WAL')
        await self.conn.execute('PRAGMA foreign_keys=ON')
        await self.conn.execute('PRAGMA busy_timeout=5000')
        await self.conn.commit()
        log.info('Database opened at %s', self.path)

    async def close(self) -> None:
        if self.conn:
            await self.conn.close(); self.conn = None; log.info('Database closed')

    def _conn(self) -> aiosqlite.Connection:
        if not self.conn: raise RuntimeError('Database is not open')
        return self.conn

    async def execute(self, sql: str, params: Iterable[Any]=()) -> aiosqlite.Cursor:
        cur = await self._conn().execute(sql, tuple(params)); await self._conn().commit(); return cur
    async def executemany(self, sql: str, seq: Iterable[Iterable[Any]]) -> None:
        await self._conn().executemany(sql, seq); await self._conn().commit()
    async def fetchone(self, sql: str, params: Iterable[Any]=()) -> aiosqlite.Row | None:
        cur = await self._conn().execute(sql, tuple(params)); return await cur.fetchone()
    async def fetchall(self, sql: str, params: Iterable[Any]=()) -> list[aiosqlite.Row]:
        cur = await self._conn().execute(sql, tuple(params)); return await cur.fetchall()
    async def executescript(self, script: str) -> None:
        await self._conn().executescript(script); await self._conn().commit()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[aiosqlite.Connection]:
        conn = self._conn()
        try:
            await conn.execute('BEGIN')
            yield conn
        except Exception:
            await conn.rollback(); raise
        else:
            await conn.commit()

    async def apply_migrations(self, migrations_dir: Path = Path('migrations')) -> None:
        await self.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
        for path in sorted(migrations_dir.glob('*.sql')):
            version = path.stem
            if await self.fetchone('SELECT version FROM schema_migrations WHERE version=?', (version,)):
                continue
            log.info('Applying migration %s', path)
            async with self.transaction() as conn:
                await conn.executescript(path.read_text(encoding='utf-8'))
                await conn.execute('INSERT INTO schema_migrations(version) VALUES (?)', (version,))
