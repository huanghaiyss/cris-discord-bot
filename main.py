from __future__ import annotations

import asyncio

from core.bot import EverythingBot
from core.config import Config, ConfigError
from core.logging import setup_logging


async def async_main() -> None:
    config = Config.from_env()
    setup_logging(config.log_level)
    bot = EverythingBot(config)
    async with bot:
        await bot.start(config.discord_token)


def main() -> None:
    try:
        asyncio.run(async_main())
    except ConfigError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc


if __name__ == "__main__":
    main()
