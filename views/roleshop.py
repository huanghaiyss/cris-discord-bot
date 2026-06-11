import discord
class RoleShopView(discord.ui.View):
    def __init__(self, bot): super().__init__(timeout=None); self.bot=bot
