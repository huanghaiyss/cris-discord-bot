from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

class ConfigError(RuntimeError):
    pass

def _parse_ids(raw: str | None) -> set[int]:
    if not raw:
        return set()
    ids: set[int] = set()
    for part in raw.split(','):
        part = part.strip()
        if part:
            ids.add(int(part))
    return ids

@dataclass(frozen=True)
class Config:
    discord_token: str
    database_path: Path = Path('data/bot.db')
    dev_guild_id: int | None = None
    owner_ids: set[int] | None = None
    default_prefix: str = '!'
    log_level: str = 'INFO'

    @classmethod
    def from_env(cls) -> 'Config':
        load_dotenv()
        token = os.getenv('DISCORD_TOKEN')
        if not token or token.strip() in {'', 'replace_with_your_bot_token'}:
            raise ConfigError('DISCORD_TOKEN is missing. Copy .env.example to .env and set it locally.')
        dev = os.getenv('DEV_GUILD_ID') or None
        return cls(
            discord_token=token.strip(),
            database_path=Path(os.getenv('DATABASE_PATH', 'data/bot.db')),
            dev_guild_id=int(dev) if dev else None,
            owner_ids=_parse_ids(os.getenv('OWNER_IDS')),
            default_prefix=os.getenv('DEFAULT_PREFIX', '!'),
            log_level=os.getenv('LOG_LEVEL', 'INFO').upper(),
        )

    @classmethod
    def from_mapping(cls, data: dict[str, str]) -> 'Config':
        token = data.get('DISCORD_TOKEN')
        if not token:
            raise ConfigError('DISCORD_TOKEN is missing.')
        dev = data.get('DEV_GUILD_ID') or None
        return cls(token, Path(data.get('DATABASE_PATH', 'data/bot.db')), int(dev) if dev else None, _parse_ids(data.get('OWNER_IDS')), data.get('DEFAULT_PREFIX', '!'), data.get('LOG_LEVEL', 'INFO').upper())
