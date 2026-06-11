import discord
from discord import app_commands
from discord.ext import commands

from core.checks import is_owner
from core.embeds import info, success
from core.interactions import safe_defer, safe_send


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="admin", description="Owner maintenance commands")

    @group.command(name="sync")
    @is_owner()
    async def sync(self, interaction: discord.Interaction):
        if not await safe_defer(interaction, ephemeral=True):
            return
        synced = await self.bot.tree.sync(guild=interaction.guild if self.bot.config.dev_guild_id else None)
        await safe_send(interaction, embed=success(f"Synced {len(synced)} commands."), ephemeral=True)

    @group.command(name="reload_cog")
    @is_owner()
    async def reload_cog(self, interaction: discord.Interaction, name: str):
        if not await safe_defer(interaction, ephemeral=True):
            return
        await self.bot.reload_extension(name if name.startswith("cogs.") else f"cogs.{name}")
        await safe_send(interaction, embed=success(f"Reloaded {name}"), ephemeral=True)

    @group.command(name="load_cog")
    @is_owner()
    async def load_cog(self, interaction: discord.Interaction, name: str):
        if not await safe_defer(interaction, ephemeral=True):
            return
        await self.bot.load_extension(name if name.startswith("cogs.") else f"cogs.{name}")
        await safe_send(interaction, embed=success(f"Loaded {name}"), ephemeral=True)

    @group.command(name="unload_cog")
    @is_owner()
    async def unload_cog(self, interaction: discord.Interaction, name: str):
        if not await safe_defer(interaction, ephemeral=True):
            return
        await self.bot.unload_extension(name if name.startswith("cogs.") else f"cogs.{name}")
        await safe_send(interaction, embed=success(f"Unloaded {name}"), ephemeral=True)

    @group.command(name="set_log_channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await safe_defer(interaction, ephemeral=True):
            return
        await self.bot.db.execute(
            "INSERT INTO guild_config(guild_id,mod_log_channel_id) VALUES (?,?) "
            "ON CONFLICT(guild_id) DO UPDATE SET mod_log_channel_id=excluded.mod_log_channel_id",
            (interaction.guild_id, channel.id),
        )
        await safe_send(interaction, embed=success(f"Mod log: {channel.mention}"), ephemeral=True)

    @group.command(name="set_prefix")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_prefix(self, interaction: discord.Interaction, prefix: str):
        if not await safe_defer(interaction, ephemeral=True):
            return
        await self.bot.db.execute(
            "INSERT INTO guild_config(guild_id,prefix) VALUES (?,?) "
            "ON CONFLICT(guild_id) DO UPDATE SET prefix=excluded.prefix",
            (interaction.guild_id, prefix),
        )
        await safe_send(interaction, embed=success(f"Prefix set to `{prefix}`"), ephemeral=True)

    @group.command(name="stats")
    @is_owner()
    async def stats(self, interaction: discord.Interaction):
        if not await safe_defer(interaction, ephemeral=True):
            return
        await safe_send(
            interaction,
            embed=info(f"Guilds: {len(self.bot.guilds)}\nLatency: {self.bot.latency * 1000:.0f} ms"),
            ephemeral=True,
        )

    @group.command(name="shutdown")
    @is_owner()
    async def shutdown(self, interaction: discord.Interaction):
        if await safe_defer(interaction, ephemeral=True):
            await safe_send(interaction, embed=success("Shutting down."), ephemeral=True)
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Admin(bot))
