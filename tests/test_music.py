"""Unit tests for Music cog voice channel state checks."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from discord.ext import commands

from cogs.music import Music


@pytest.fixture
def bot():
    return MagicMock(spec=commands.Bot)


@pytest.fixture
def ctx():
    mock_ctx = MagicMock()
    mock_ctx.guild = MagicMock()
    mock_ctx.guild.id = 123456
    mock_ctx.send = AsyncMock()
    mock_ctx.typing = AsyncMock()
    mock_ctx.author = MagicMock()
    mock_ctx.author.voice = MagicMock()
    mock_ctx.author.voice.channel = MagicMock()
    mock_ctx.voice_client = None
    return mock_ctx


def test_play_next_not_connected(bot, ctx):
    music = Music(bot)
    ctx.voice_client = None
    music.get_queue(ctx.guild.id).append("test_song")
    # Should send error if not connected
    import asyncio

    asyncio.run(music.play_next(ctx))
    ctx.send.assert_called_with("❌ Bot is not connected to a voice channel.")


def test_play_next_empty_queue(bot, ctx):
    music = Music(bot)
    ctx.voice_client = MagicMock()
    ctx.voice_client.is_connected.return_value = True
    # Should send nothing if queue is empty
    import asyncio

    asyncio.run(music.play_next(ctx))
    ctx.send.assert_not_called()


def test_play_command_author_not_in_voice(bot, ctx):
    music = Music(bot)
    ctx.author.voice = None
    import asyncio

    asyncio.run(Music.play(music, ctx, query="test_song"))
    ctx.send.assert_called_with(
        "❌ You must be connected to a voice channel to use this command."
    )


def test_play_command_bot_in_different_channel(bot, ctx):
    music = Music(bot)
    ctx.voice_client = MagicMock()
    ctx.voice_client.is_connected.return_value = True
    ctx.voice_client.channel = MagicMock()
    ctx.voice_client.channel.name = "Music"
    ctx.author.voice.channel.name = "General"
    # Ensure bot and author are in different channels
    assert ctx.voice_client.channel != ctx.author.voice.channel
    import asyncio

    asyncio.run(Music.play(music, ctx, query="test_song"))
    ctx.send.assert_called_with(
        "❌ Bot is in a different channel: Music. Please join the same channel."
    )


def test_stop_not_connected(bot, ctx):
    music = Music(bot)
    ctx.voice_client = None
    import asyncio

    asyncio.run(Music.stop(music, ctx))
    ctx.send.assert_called_with("❌ Bot is not connected to a voice channel.")


def test_stop_connected(bot, ctx):
    music = Music(bot)
    ctx.voice_client = MagicMock()
    ctx.voice_client.is_connected.return_value = True
    from unittest.mock import AsyncMock

    ctx.voice_client.disconnect = AsyncMock()
    import asyncio

    asyncio.run(Music.stop(music, ctx))
    ctx.voice_client.disconnect.assert_called()
    ctx.send.assert_called_with("Disconnected from the voice channel.")
