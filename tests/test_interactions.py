import discord

from core.bot import EverythingBot
from core.config import Config
from core.interactions import interaction_context, safe_send
from core.tree import LoggedCommandTree


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
        self.channel_id = 789
        self.user = type("User", (), {"id": 456, "__str__": lambda self: "debug-user#0001"})()
        self.guild = type("Guild", (), {"name": "Debug Guild"})()
        self.channel = type("Channel", (), {"id": 789, "name": "debug-channel"})()
        self.id = 999
        self.type = discord.InteractionType.application_command
        self.data = {
            "name": "debug",
            "options": [
                {"name": "normal", "type": 3, "value": "hello"},
                {"name": "secret", "type": 3, "value": "MTIzNDU2Nzg5MDEyMzQ1Njc4OTAx.ABCDEF.abcdefghijklmnopqrstuvwxyz"},
            ],
        }


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


def test_interaction_context_logs_command_user_options_and_redacts_token_like_values():
    ctx = interaction_context(DummyInteraction())
    assert ctx["interaction_id"] == 999
    assert ctx["command"] == "debug"
    assert ctx["guild_id"] == 123
    assert ctx["channel_id"] == 789
    assert ctx["user_id"] == 456
    assert ctx["options"][0]["value"] == "hello"
    assert ctx["options"][1]["value"] == "[redacted-token-like-value]"


def test_bot_uses_logged_command_tree():
    bot = EverythingBot(Config.from_mapping({"DISCORD_TOKEN": "dummy", "DATABASE_PATH": "data/test-tree.db", "OWNER_IDS": "123"}))
    try:
        assert isinstance(bot.tree, LoggedCommandTree)
    finally:
        # No network session is opened by construction, but close keeps discord.py tidy.
        pass
