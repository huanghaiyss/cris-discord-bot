# discord_everything_bot

A real modular Discord community bot built with Python, discord.py 2.x slash commands, aiosqlite, and cogs. It is designed as an all-in-one community bot inspired by moderation, ticket, economy, leveling, starboard, suggestion, and utility bots.

## Features

- Administration: command sync, cog load/reload/unload, stats, shutdown, log channel, prefix storage.
- Moderation: warn, warnings, clear warnings, timeout/remove timeout, kick, ban, unban, case lookup, per-guild case numbers, modlog storage.
- Automod: enable/disable, spam/repeated message/mention checks, invite filtering, link filtering, violation logging, possible ghost-ping logging, panic-mode config flag.
- Economy: fake in-server coins only, balance, daily, work, pay, slots, blackjack, inventory, leaderboard, admin give/take.
- Leveling: XP on messages, cooldowns, rank, leaderboard, enable/disable, level-up channel, role rewards.
- Utility: ping, user/server/avatar/bot/channel/role/invite info, polls.
- Tickets: persistent button panel, private channels, close button, add/remove users, category/log config, database records.
- Starboard: star reaction tracking, threshold, duplicate prevention, stored starboard mappings.
- Suggestions: submit suggestions, persistent vote buttons, one vote per user with change support, status updates.
- Role shop: admins sell roles for fake coins; users buy roles with hierarchy validation.
- Fun: coinflip, dice, eightball, rock-paper-scissors, trivia, meme text, choose.

## Requirements

- Python 3.11+
- A Discord bot application
- `uv` recommended, or standard `python -m venv`

Dependencies are in `requirements.txt` and `pyproject.toml`:

- discord.py 2.x
- python-dotenv
- aiosqlite
- pytest / pytest-asyncio for tests

## Discord Developer Portal setup

1. Create an application at <https://discord.com/developers/applications>.
2. Create a bot user.
3. Copy the token locally into `.env`. Do **not** paste it into chat or commit it.
4. Enable privileged intents:
   - Server Members Intent: required for member, role, moderation, tickets, and user info features.
   - Message Content Intent: required for automod and leveling message listeners.
   - Presence Intent: optional; this project does not currently require it, but `Intents.all()` requests it if enabled.
5. Invite the bot with `applications.commands` and the permissions needed for your selected features. Administrator works for private/testing servers, but the code still checks permissions and role hierarchy.

## Installation with uv

```bash
cd /data/data/com.termux/files/home/acheng/code/discord-everything-bot
uv venv --python python
uv pip install -r requirements.txt
```

Alternative:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Environment setup

```bash
cp .env.example .env
# edit .env locally and set DISCORD_TOKEN
```

Supported variables:

- `DISCORD_TOKEN`: required. Loaded with `os.getenv("DISCORD_TOKEN")` after `python-dotenv` loads `.env`.
- `DATABASE_PATH`: optional, defaults to `data/bot.db`.
- `DEV_GUILD_ID`: optional guild ID for faster slash command sync during development.
- `OWNER_IDS`: optional comma-separated Discord user IDs for `/admin` owner commands.
- `DEFAULT_PREFIX`: optional fallback text prefix, defaults to `!`.
- `LOG_LEVEL`: optional, defaults to `INFO`.

## Run

```bash
cd /data/data/com.termux/files/home/acheng/code/discord-everything-bot
uv run python main.py
```

If you activated `.venv` manually:

```bash
python main.py
```

On first startup the bot:

1. Loads `.env`.
2. Opens SQLite at `data/bot.db` unless overridden.
3. Enables WAL and foreign keys.
4. Applies `migrations/001_initial.sql`.
5. Discovers and loads all cogs from `cogs/`.
6. Registers persistent ticket/suggestion/role-shop views.
7. Syncs slash commands to `DEV_GUILD_ID` if set, otherwise globally.

Global slash command sync can take time to appear in Discord. Use `DEV_GUILD_ID` while developing.

## Test and validation

```bash
uv run python -m compileall .
uv run python -m pytest
```

## Database

SQLite is accessed asynchronously through `core/database.py` using aiosqlite. The migration creates tables for guild config, command logs, moderation cases, warnings, automod, economy, inventory, leveling, rewards, tickets, starboard, suggestions, and role shop.

Runtime database files are ignored by git: `data/*.db`, `data/*.db-*`.

## Command list

- `/admin sync|reload_cog|load_cog|unload_cog|set_log_channel|set_prefix|stats|shutdown`
- `/mod warn|warnings|clear_warnings|timeout|remove_timeout|kick|ban|unban|case|cases|set_modlog`
- `/automod status|enable|disable|config|set_log_channel|set_spam_threshold|set_mention_threshold|toggle_invite_filter|toggle_link_filter|panic_enable|panic_disable`
- `/economy balance|daily|work|pay|slots|blackjack|inventory|leaderboard|shop|buy|give|take`
- `/level rank|leaderboard|set_channel|set_reward|remove_reward|rewards|disable|enable`
- `/utility ping|userinfo|serverinfo|avatar|botinfo|channelinfo|roleinfo|invite_info|poll`
- `/ticket panel|close|add_user|remove_user|config_category|config_log_channel`
- `/starboard enable|disable|config|ignore_channel|unignore_channel`
- `/suggest submit|channel|status`
- `/roleshop list|buy|add|remove`
- `/fun coinflip|dice|eightball|rps|trivia|meme_text|choose`

## Security notes

- Never commit `.env` or tokens.
- Economy gambling uses fake in-server currency only.
- The bot does not implement self-bot behavior, mass DM spam, raid tools, phishing, token grabbing, malware, spyware, or real-money gambling.
- User-facing errors are concise; internal exceptions are logged.
- Moderation and admin commands use Discord permission checks and hierarchy checks where applicable.

## Troubleshooting

- `Configuration error: DISCORD_TOKEN is missing`: create `.env` from `.env.example` and set the token locally.
- Slash commands do not appear: set `DEV_GUILD_ID` for instant guild sync or wait for global sync propagation.
- Permission errors: check bot invite permissions and role hierarchy. The bot role must be above roles/members it manages.
- Automod/leveling not firing: enable Message Content Intent in the Developer Portal and ensure the bot can read/send/manage messages.
- Tickets fail to create: verify the bot can manage channels and that configured category permissions are valid.
