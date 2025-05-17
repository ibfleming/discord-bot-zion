# cogs/music.py

import re
from discord.ext import commands
from core.ytdl import YTDLSource
from loguru import logger


def is_youtube_url(string):
    youtube_regex = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
    return bool(youtube_regex.match(string))


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, query):
        async with ctx.typing():
            try:
                if is_youtube_url(query):
                    player = await YTDLSource.from_url(
                        query, loop=self.bot.loop, stream=True
                    )
                else:
                    player = await YTDLSource.from_string(
                        query, loop=self.bot.loop, stream=True
                    )

                ctx.voice_client.play(
                    player,
                    after=lambda e: logger.error(f"Player error: {e}") if e else None,
                )
                await ctx.send(f"Now playing: {player.title}")
                logger.info(f"Now playing: {player.title}")
            except Exception as e:
                await ctx.send("An error occurred while trying to play the song.")
                logger.error(f"Error in play command: {e}")

    @commands.command()
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")
        logger.info(f"Volume changed to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
            logger.info("Disconnected from the voice channel.")
        else:
            await ctx.send("Not connected to a voice channel.")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                logger.info(
                    f"Connected to voice channel: {ctx.author.voice.channel.name}"
                )
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            logger.info("Stopped the current playing audio.")
