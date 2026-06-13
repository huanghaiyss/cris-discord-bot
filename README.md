Discord Everything Bot

A modular Discord community bot built with Python and "discord.py".

This project includes common server tools such as moderation, automod, tickets, economy, leveling, starboard, suggestions, role shop, and utility commands. It is designed to be easy to run, easy to extend, and organized around Discord slash commands and cogs.

Features

Administration

- Sync slash commands
- Load, reload, and unload cogs
- Configure log channels
- Configure command prefix
- View bot statistics
- Shut down the bot safely

Moderation

- Warn users
- View and clear warnings
- Timeout and remove timeout
- Kick, ban, and unban users
- View moderation cases
- Per-server case numbers
- Modlog support

Automod

- Enable or disable automod
- Spam detection
- Repeated message checks
- Mention spam checks
- Invite filtering
- Link filtering
- Violation logging
- Optional panic mode flag

Economy

- Fake in-server coins
- Balance checking
- Daily rewards
- Work command
- Pay other users
- Slots
- Blackjack
- Inventory
- Leaderboard
- Admin give and take commands

This economy system is only for Discord server fun. It does not use real money.

Leveling

- XP from messages
- Cooldowns to prevent spam farming
- Rank command
- Leaderboard
- Enable or disable leveling
- Level-up channel
- Role rewards

Tickets

- Persistent ticket panel
- Private ticket channels
- Close button
- Add or remove users from tickets
- Category configuration
- Ticket log channel
- Database records

Starboard

- Track star reactions
- Configurable star threshold
- Duplicate prevention
- Stored message mappings

Suggestions

- Submit suggestions
- Vote buttons
- One vote per user
- Vote changes supported
- Update suggestion status

Role Shop

- Admins can sell roles for server coins
- Users can buy roles
- Role hierarchy checks included

Utility and Fun

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

Requirements

- Python 3.11 or newer
- A Discord bot application
- "uv" or a standard Python virtual environment

Main dependencies:

- "discord.py"
- "python-dotenv"
- "aiosqlite"
- "pytest"
- "pytest-asyncio"

Dependencies are listed in:

requirements.txt
pyproject.toml

Discord Developer Portal Setup

1. Go to the Discord Developer Portal:
   
   https://discord.com/developers/applications

2. Create a new application.

3. Add a bot user to the application.

4. Reset or copy the bot token.

5. Create a local ".env" file and put the token there.
   
   Do not commit the token. Do not paste it into public chats, issues, screenshots, logs, or README files.

6. Enable the required privileged intents:
   
   - Server Members Intent
   - Message Content Intent
   
   Message Content Intent is required for features like automod and leveling.

7. Invite the bot to your server with:
   
   - "bot"
   - "applications.commands"
   
   For testing on a private server, Administrator permission is the easiest option. For production, use only the permissions required by the features you enable.

Installation

Clone the repository:

git clone https://github.com/YOUR_USERNAME/discord-everything-bot.git
cd discord-everything-bot

Create a virtual environment with "uv":

uv venv --python python
uv pip install -r requirements.txt

Or use the standard Python virtual environment workflow:

python -m venv .venv

Activate it on Linux/macOS:

source .venv/bin/activate

Activate it on Windows PowerShell:

.venv\Scripts\Activate.ps1

Then install dependencies:

pip install -r requirements.txt

Environment Setup

Copy the example environment file:

cp .env.example .env

Edit ".env" and set your bot token:

DISCORD_TOKEN=your_bot_token_here

Supported environment variables:

DISCORD_TOKEN=
DATABASE_PATH=data/bot.db
DEV_GUILD_ID=
OWNER_IDS=
DEFAULT_PREFIX=!
LOG_LEVEL=INFO

Environment Variables

Variable| Required| Description
"DISCORD_TOKEN"| Yes| Discord bot token
"DATABASE_PATH"| No| SQLite database path. Defaults to "data/bot.db"
"DEV_GUILD_ID"| No| Guild ID for faster slash command syncing during development
"OWNER_IDS"| No| Comma-separated Discord user IDs for owner-only admin commands
"DEFAULT_PREFIX"| No| Default text command prefix. Defaults to "!"
"LOG_LEVEL"| No| Logging level. Defaults to "INFO"

Running the Bot

With "uv":

uv run python main.py

With an activated virtual environment:

python main.py

On first startup, the bot will:

1. Load environment variables from ".env"
2. Open the SQLite database
3. Enable SQLite WAL mode and foreign keys
4. Apply database migrations
5. Load all cogs from the "cogs/" folder
6. Register persistent ticket, suggestion, and role shop views
7. Sync slash commands

If "DEV_GUILD_ID" is set, slash commands sync faster for that server.

If "DEV_GUILD_ID" is not set, commands are synced globally. Global command updates can take longer to appear in Discord.

Testing

Run a basic compile check:

python -m compileall .

Run tests:

python -m pytest

Or with "uv":

uv run python -m compileall .
uv run python -m pytest

Database

The bot uses SQLite through "aiosqlite".

Database logic is handled in:

core/database.py

The initial migration is stored in:

migrations/001_initial.sql

The database stores data for:

- Guild config
- Command logs
- Moderation cases
- Warnings
- Automod settings
- Economy balances
- Inventory
- Leveling
- Level rewards
- Tickets
- Starboard
- Suggestions
- Role shop

Runtime database files are ignored by git:

data/*.db
data/*.db-*

Command Overview

Admin

/admin sync
/admin reload_cog
/admin load_cog
/admin unload_cog
/admin set_log_channel
/admin set_prefix
/admin stats
/admin shutdown

Moderation

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

Automod

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

Economy

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

Leveling

/level rank
/level leaderboard
/level set_channel
/level set_reward
/level remove_reward
/level rewards
/level disable
/level enable

Utility

/utility ping
/utility userinfo
/utility serverinfo
/utility avatar
/utility botinfo
/utility channelinfo
/utility roleinfo
/utility invite_info
/utility poll

Tickets

/ticket panel
/ticket close
/ticket add_user
/ticket remove_user
/ticket config_category
/ticket config_log_channel

Starboard

/starboard enable
/starboard disable
/starboard config
/starboard ignore_channel
/starboard unignore_channel

Suggestions

/suggest submit
/suggest channel
/suggest status

Role Shop

/roleshop list
/roleshop buy
/roleshop add
/roleshop remove

Fun

/fun coinflip
/fun dice
/fun eightball
/fun rps
/fun trivia
/fun meme_text
/fun choose

Security Notes

- Never commit ".env".
- Never commit Discord bot tokens.
- If a token is exposed, reset it immediately in the Discord Developer Portal.
- Keep production tokens separate from testing tokens.
- Use least-privilege permissions for production servers.
- Keep the bot role below owner/admin roles that it should not manage.
- Do not log secrets.
- Do not upload local database files if they contain server data.

This bot does not include:

- Self-bot behavior
- Token grabbing
- Malware
- Spyware
- Phishing tools
- Raid tools
- Mass DM spam
- Real-money gambling

Moderation and admin commands use Discord permission checks and role hierarchy checks where needed.

Troubleshooting

"Configuration error: DISCORD_TOKEN is missing"

Create ".env" from ".env.example" and set "DISCORD_TOKEN".

cp .env.example .env

Then edit ".env".

Slash commands do not appear

For development, set "DEV_GUILD_ID" in ".env" so commands sync directly to your test server.

Global slash commands can take time to update.

Permission errors

Check:

- The bot invite permissions
- The bot role position
- Channel permissions
- Server role hierarchy

The bot role must be higher than the roles or members it needs to manage.

Automod or leveling does not work

Check that Message Content Intent is enabled in the Discord Developer Portal.

Also make sure the bot can:

- Read messages
- Send messages
- Manage messages if automod actions require it

Tickets fail to create

Check that the bot can:

- Manage channels
- View the configured category
- Create private channels
- Manage permissions in that category

Database errors

Make sure the bot can write to the "data/" folder.

If you changed migrations manually during development, delete the local test database and restart the bot.

Do not delete a production database unless you have a backup.

Development Notes

The project is organized around cogs so features can be worked on separately.

Typical places to edit:

cogs/
core/
migrations/
tests/

When adding a new feature:

1. Add or update the cog.
2. Add database changes if needed.
3. Add or update tests.
4. Run compile checks.
5. Run the test suite.
6. Test slash commands in a development server.

License

Add your license here before publishing the repository.