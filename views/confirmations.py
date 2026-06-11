import discord
class ConfirmView(discord.ui.View):
    def __init__(self, timeout=30): super().__init__(timeout=timeout); self.value=None
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.danger)
    async def confirm(self, interaction:discord.Interaction, button:discord.ui.Button): self.value=True; await interaction.response.defer(); self.stop()
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction:discord.Interaction, button:discord.ui.Button): self.value=False; await interaction.response.defer(); self.stop()
