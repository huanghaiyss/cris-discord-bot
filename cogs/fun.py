import random

from discord import app_commands
from discord.ext import commands

from core.embeds import make_embed
from core.interactions import safe_defer, safe_send


class Fun(commands.Cog):
    group = app_commands.Group(name="fun", description="Safe fun commands")

    def __init__(self, bot):
        self.bot = bot

    @group.command(name="coinflip")
    async def coinflip(self, i):
        if not await safe_defer(i, ephemeral=False):
            return
        await safe_send(i, embed=make_embed("Coinflip", random.choice(["Heads", "Tails"]), "info"), ephemeral=False)

    @group.command(name="dice")
    async def dice(self, i, sides: app_commands.Range[int, 2, 1000] = 6, count: app_commands.Range[int, 1, 20] = 1):
        if not await safe_defer(i, ephemeral=False):
            return
        rolls = [random.randint(1, sides) for _ in range(count)]
        await safe_send(i, embed=make_embed("Dice", f"{rolls}\nTotal: {sum(rolls)}", "info"), ephemeral=False)

    @group.command(name="eightball")
    async def eightball(self, i, question: str):
        if not await safe_defer(i, ephemeral=False):
            return
        await safe_send(i, embed=make_embed("8 Ball", random.choice(["Yes.", "No.", "Maybe.", "Ask later.", "Definitely."]), "info"), ephemeral=False)

    @group.command(name="rps")
    async def rps(self, i, choice: str):
        if not await safe_defer(i, ephemeral=False):
            return
        bot = random.choice(["rock", "paper", "scissors"])
        await safe_send(i, embed=make_embed("RPS", f"You: {choice.lower()}\nBot: {bot}", "info"), ephemeral=False)

    @group.command(name="trivia")
    async def trivia(self, i):
        if not await safe_defer(i, ephemeral=False):
            return
        await safe_send(i, embed=make_embed("Trivia", "Question: What protocol does Discord use for realtime gateway events?\nAnswer: WebSocket.", "info"), ephemeral=False)

    @group.command(name="meme_text")
    async def meme_text(self, i, text: str):
        if not await safe_defer(i, ephemeral=False):
            return
        await safe_send(i, text.upper()[:1900], ephemeral=False)

    @group.command(name="choose")
    async def choose(self, i, options: str):
        if not await safe_defer(i, ephemeral=False):
            return
        opts = [o.strip() for o in options.split("|") if o.strip()]
        await safe_send(i, embed=make_embed("Choose", random.choice(opts) if opts else "No options.", "info"), ephemeral=False)


async def setup(bot):
    await bot.add_cog(Fun(bot))
