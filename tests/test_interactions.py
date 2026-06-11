import discord

from core.interactions import safe_send


class DummyResponse:
    def __init__(self, done: bool = False):
        self.done = done
        self.kwargs = None

    def is_done(self):
        return self.done

    async def send_message(self, **kwargs):
        self.kwargs = kwargs


class DummyFollowup:
    def __init__(self):
        self.kwargs = None

    async def send(self, **kwargs):
        self.kwargs = kwargs


class DummyInteraction:
    def __init__(self, done: bool = False):
        self.response = DummyResponse(done)
        self.followup = DummyFollowup()
        self.command = None
        self.guild_id = 123
        self.user = type("User", (), {"id": 456})()


async def test_safe_send_does_not_mix_embed_and_embeds_on_initial_response():
    interaction = DummyInteraction(done=False)
    ok = await safe_send(interaction, embed=discord.Embed(title="ok"), ephemeral=True)
    assert ok is True
    assert "embed" in interaction.response.kwargs
    assert "embeds" not in interaction.response.kwargs


async def test_safe_send_does_not_mix_embed_and_embeds_on_followup_response():
    interaction = DummyInteraction(done=True)
    ok = await safe_send(interaction, embed=discord.Embed(title="ok"), ephemeral=True)
    assert ok is True
    assert "embed" in interaction.followup.kwargs
    assert "embeds" not in interaction.followup.kwargs
