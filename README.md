# Discord Everything Bot

A modular Discord bot built with Python and `discord.py`.

This bot includes common community-server features such as moderation, automod, tickets, economy, leveling, starboard, suggestions, role shop, utility commands, and simple fun commands. The project is organized with cogs so each feature can be maintained separately.

## Features

### Administration

- Sync slash commands
- Load, reload, and unload cogs
- Configure log channels
- Configure command prefix
- View bot statistics
- Shut down the bot safely

### Moderation

- Warn users
- View warning history
- Clear warnings
- Timeout and remove timeout
- Kick, ban, and unban users
- View moderation cases
- Store per-server case numbers
- Send moderation logs to a configured channel

### Automod

- Enable or disable automod
- Detect spam
- Detect repeated messages
- Detect mention spam
- Filter invite links
- Filter normal links
- Log automod violations
- Configure panic mode

### Economy

- Server-only fake coins
- Balance command
- Daily rewards
- Work command
- Pay other users
- Slots
- Blackjack
- Inventory
- Leaderboard
- Admin give and take commands

The economy system is only for in-server fun. It does not use real money.

### Leveling

- XP from messages
- Cooldowns to reduce spam farming
- Rank command
- Level leaderboard
- Level-up channel configuration
- Role rewards
- Enable or disable leveling per server

### Tickets

- Persistent ticket panel
- Private ticket channels
- Close ticket button
- Add or remove users from tickets
- Configure ticket category
- Configure ticket log channel
- Store ticket records in the database

### Starboard

- Track star reactions
- Configurable star threshold
- Prevent duplicate starboard posts
- Store starboard message mappings

### Suggestions

- Submit suggestions
- Persistent vote buttons
- One vote per user
- Users can change their vote
- Update suggestion status

### Role Shop

- Sell roles for server coins
- Buy roles with fake currency
- Validate role hierarchy
- Admin commands for adding and removing shop roles

### Utility and Fun

- Ping
- User info
- Server info
- Avatar
- Bot info
- Channel info
- Role info
- Invite info
- Polls
- Coinflip
- Dice
- Eightball
- Rock-paper-scissors
- Trivia
- Meme text
- Random choice

## Requirements

- Python 3.11 or newer
- A Discord bot application
- `uv` or a standard Python virtual environment

Main dependencies:

- `discord.py`
- `python-dotenv`
- `aiosqlite`
- `pytest`
- `pytest-asyncio`

Dependencies are listed in:

```text
requirements.txt
pyproject.toml
```

## Discord Bot Setup

Create a Discord application from the Discord Developer Portal:

```text
https://discord.com/developers/applications
```

Then:

1. Create a new application.
2. Add a bot user.
3. Copy the bot token.
4. Enable the required privileged intents:
   - Server Members Intent
   - Message Content Intent
5. Invite the bot to your server with:
   - `bot`
   - `applications.commands`

For a private test server, Administrator permission is the simplest option. For a production server, use only the permissions required by the features you plan to enable.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/discord-everything-bot.git
cd discord-everything-bot
```

Create a virtual environment with `uv`:

```bash
uv venv --python python
uv pip install -r requirements.txt
```

Or use the standard Python virtual environment workflow:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your bot token:

```env
DISCORD_TOKEN=your_bot_token_here
```

Supported variables:

| Variable | Required | Description |
|---|---:|---|
| `DISCORD_TOKEN` | Yes | Discord bot token |
| `DATABASE_PATH` | No | SQLite database path. Defaults to `data/bot.db` |
| `DEV_GUILD_ID` | No | Guild ID for faster slash command syncing during development |
| `OWNER_IDS` | No | Comma-separated Discord user IDs for owner-only admin commands |
| `DEFAULT_PREFIX` | No | Default text command prefix. Defaults to `!` |
| `LOG_LEVEL` | No | Logging level. Defaults to `INFO` |

Example:

```env
DISCORD_TOKEN=your_bot_token_here
DATABASE_PATH=data/bot.db
DEV_GUILD_ID=
OWNER_IDS=
DEFAULT_PREFIX=!
LOG_LEVEL=INFO
```

## Running the Bot

With `uv`:

```bash
uv run python main.py
```

With an activated virtual environment:

```bash
python main.py
```

On startup, the bot will:

1. Load environment variables from `.env`
2. Open the SQLite database
3. Enable SQLite WAL mode and foreign keys
4. Apply database migrations
5. Load all cogs from the `cogs/` directory
6. Register persistent views for tickets, suggestions, and role shop
7. Sync slash commands

If `DEV_GUILD_ID` is set, slash commands sync directly to that server and usually appear much faster.

If `DEV_GUILD_ID` is not set, commands are synced globally. Global command updates can take longer to appear in Discord.

## Testing

Run a compile check:

```bash
python -m compileall .
```

Run the test suite:

```bash
python -m pytest
```

Or with `uv`:

```bash
uv run python -m compileall .
uv run python -m pytest
```

## Database

The bot uses SQLite through `aiosqlite`.

Database setup is handled in:

```text
core/database.py
```

The initial migration is stored in:

```text
migrations/001_initial.sql
```

The database stores:

- Guild configuration
- Command logs
- Moderation cases
- Warnings
- Automod settings
- Economy balances
- Inventory
- Leveling data
- Level rewards
- Tickets
- Starboard messages
- Suggestions
- Role shop entries

Runtime database files are ignored by git:

```text
data/*.db
data/*.db-*
```

## Project Structure

```text
discord-everything-bot/
├── cogs/
├── core/
├── data/
├── migrations/
├── tests/
├── .env.example
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Command Overview

### Admin

```text
/admin sync
/admin reload_cog
/admin load_cog
/admin unload_cog
/admin set_log_channel
/admin set_prefix
/admin stats
/admin shutdown
```

### Moderation

```text
/mod warn
/mod warnings
/mod clear_warnings
/mod timeout
/mod remove_timeout
/mod kick
/mod ban
/mod unban
/mod case
/mod cases
/mod set_modlog
```

### Automod

```text
/automod status
/automod enable
/automod disable
/automod config
/automod set_log_channel
/automod set_spam_threshold
/automod set_mention_threshold
/automod toggle_invite_filter
/automod toggle_link_filter
/automod panic_enable
/automod panic_disable
```

### Economy

```text
/economy balance
/economy daily
/economy work
/economy pay
/economy slots
/economy blackjack
/economy inventory
/economy leaderboard
/economy shop
/economy buy
/economy give
/economy take
```

### Leveling

```text
/level rank
/level leaderboard
/level set_channel
/level set_reward
/level remove_reward
/level rewards
/level disable
/level enable
```

### Utility

```text
/utility ping
/utility userinfo
/utility serverinfo
/utility avatar
/utility botinfo
/utility channelinfo
/utility roleinfo
/utility invite_info
/utility poll
```

### Tickets

```text
/ticket panel
/ticket close
/ticket add_user
/ticket remove_user
/ticket config_category
/ticket config_log_channel
```

### Starboard

```text
/starboard enable
/starboard disable
/starboard config
/starboard ignore_channel
/starboard unignore_channel
```

### Suggestions

```text
/suggest submit
/suggest channel
/suggest status
```

### Role Shop

```text
/roleshop list
/roleshop buy
/roleshop add
/roleshop remove
```

### Fun

```text
/fun coinflip
/fun dice
/fun eightball
/fun rps
/fun trivia
/fun meme_text
/fun choose
```

## Troubleshooting

### `Configuration error: DISCORD_TOKEN is missing`

Create `.env` from `.env.example` and set `DISCORD_TOKEN`.

```bash
cp .env.example .env
```

### Slash commands do not appear

Set `DEV_GUILD_ID` in `.env` while developing. Guild command sync is usually much faster than global sync.

Global slash commands can take longer to update.

### Permission errors

Check:

- Bot invite permissions
- Bot role position
- Channel permissions
- Server role hierarchy

The bot role must be higher than the roles or members it needs to manage.

### Automod or leveling does not work

Check that Message Content Intent is enabled in the Discord Developer Portal.

Also make sure the bot can:

- Read messages
- Send messages
- Manage messages if automod actions require it

### Tickets fail to create

Check that the bot can:

- Manage channels
- View the configured category
- Create private channels
- Manage permissions in that category

### Database errors

Make sure the bot can write to the `data/` directory.

If migrations changed during development, delete the local test database and restart the bot.

Do not delete a production database unless you have a backup.

## Development

The project is split into cogs so each feature can be updated separately.

Common folders:

```text
cogs/
core/
migrations/
tests/
```

Before pushing changes:

```bash
python -m compileall .
python -m pytest
```

For development servers, set `DEV_GUILD_ID` so slash commands update quickly while testing.
