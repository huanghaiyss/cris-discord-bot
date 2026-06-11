import discord

from core.interactions import safe_defer, safe_send


class SuggestionVoteView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def _vote(self, interaction: discord.Interaction, vote: int):
        from services.suggestion_service import SuggestionService

        if not interaction.message or not interaction.guild:
            await safe_send(interaction, "Missing suggestion context.", ephemeral=True)
            return
        if not await safe_defer(interaction, ephemeral=True):
            return
        row = await self.bot.db.fetchone("SELECT id FROM suggestions WHERE guild_id=? AND message_id=?", (interaction.guild.id, interaction.message.id))
        if not row:
            await safe_send(interaction, "Suggestion not found.", ephemeral=True)
            return
        svc = SuggestionService(self.bot.db)
        await svc.vote(int(row["id"]), interaction.user.id, vote)
        counts = await svc.counts(int(row["id"]))
        await safe_send(interaction, f'Vote saved. 👍 {counts["up"]} 👎 {counts["down"]}', ephemeral=True)

    @discord.ui.button(label="Upvote", emoji="👍", style=discord.ButtonStyle.success, custom_id="suggestion:up")
    async def up(self, interaction, button):
        await self._vote(interaction, 1)

    @discord.ui.button(label="Downvote", emoji="👎", style=discord.ButtonStyle.danger, custom_id="suggestion:down")
    async def down(self, interaction, button):
        await self._vote(interaction, -1)
