from __future__ import annotations
import discord

COLORS = {
    'success': discord.Color.green(), 'error': discord.Color.red(), 'warning': discord.Color.orange(),
    'info': discord.Color.blurple(), 'moderation': discord.Color.dark_red(), 'economy': discord.Color.gold(),
    'leveling': discord.Color.purple(), 'tickets': discord.Color.teal(), 'suggestions': discord.Color.blue(),
    'starboard': discord.Color.gold(),
}

def make_embed(title: str, description: str | None = None, kind: str = 'info', **kwargs) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=COLORS.get(kind, COLORS['info']), **kwargs)
    return embed

def success(msg: str, title: str='Success') -> discord.Embed: return make_embed(title, msg, 'success')
def error(msg: str, title: str='Error') -> discord.Embed: return make_embed(title, msg, 'error')
def warning(msg: str, title: str='Warning') -> discord.Embed: return make_embed(title, msg, 'warning')
def info(msg: str, title: str='Info') -> discord.Embed: return make_embed(title, msg, 'info')
