"""Music command cog for the Zion Discord Bot."""

import re
from collections import deque
from typing import Optional

import discord
from discord.ext import commands
from loguru import logger

from core.ytdl import YTDLSource


def is_youtube_url(string):
    youtube_regex = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
    return bool(youtube_regex.match(string))


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        logger.debug(f"Queue state before playing next: {list(queue)}")
        if not queue:
            logger.info("Queue is empty.")
            return

        next_query = queue.popleft()
        logger.debug(f"Next query to play: {next_query}")
        try:
            player = (
                await YTDLSource.from_url(next_query, loop=self.bot.loop, stream=True)
                if is_youtube_url(next_query)
                else await YTDLSource.from_string(
                    next_query, loop=self.bot.loop, stream=True
                )
            )
            ctx.voice_client.play(
                player,
                after=lambda e: (
                    self.bot.loop.create_task(self.play_next(ctx))
                    if not e
                    else logger.error(f"Player error: {e}")
                ),
            )
            await ctx.send(f"🎶 Now playing: {player.title}")
            logger.info(f"Now playing: {player.title}")
        except Exception as e:
            logger.exception(f"Queue playback error: {e}")
            await ctx.send("❌ Failed to play the next song.")

    @commands.group(name="queue", invoke_without_command=True)  # type: ignore[arg-type]
    async def queue_group(self, ctx: commands.Context):
        await ctx.send("Subcommands: list, add <song>, clear")

    @queue_group.command(name="list")  # type: ignore[arg-type]
    async def queue_list(self, ctx: commands.Context):
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return

        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await ctx.send("📭 Queue is empty.")
            return

        description = "\n".join(f"`{i + 1}.` {song}" for i, song in enumerate(queue))
        embed = discord.Embed(
            title="🎶 Current Queue", description=description, color=0x1DB954
        )
        await ctx.send(embed=embed)

    @queue_group.command(name="add")  # type: ignore[arg-type]
    async def queue_add(self, ctx: commands.Context, *, song: Optional[str] = None):
        if not song or not song.strip():
            await ctx.send("❌ Please provide a valid song name or URL.")
            return

        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return

        queue = self.get_queue(ctx.guild.id)
        queue.append(song)
        await ctx.send(f"✅ Added to queue: `{song}`")
        logger.info(f"Added to queue: {song}")

    @queue_group.command(name="clear")  # type: ignore[arg-type]
    async def queue_clear(self, ctx: commands.Context):
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return

        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        await ctx.send("Queue cleared.")
        logger.info("Queue cleared.")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped current track.")
            logger.info("Track skipped.")
        else:
            await ctx.send("Nothing is currently playing.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed playback.")
            logger.info("Playback resumed.")
        else:
            await ctx.send("Playback is not paused.")

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused playback.")
            logger.info("Playback paused.")
        else:
            await ctx.send("Nothing is currently playing.")

    @commands.command()
    async def play(self, ctx, *, query):
        async with ctx.typing():
            queue = self.get_queue(ctx.guild.id)
            should_play_immediately = not ctx.voice_client.is_playing() and not queue

            queue.append(query)
            logger.info(f"Queued: {query}")
            logger.debug(f"Queue state after adding: {list(queue)}")

            if not should_play_immediately:
                await ctx.send(f"✅ Added to queue: `{query}`")

            if should_play_immediately:
                await self.play_next(ctx)

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
        logger.debug("Entering ensure_voice method.")
        if ctx.voice_client is None:
            if ctx.author.voice:
                try:
                    logger.debug(
                        f"Attempting to connect to voice channel: {ctx.author.voice.channel.name}"
                    )
                    await ctx.author.voice.channel.connect()
                    logger.info(
                        f"Connected to voice channel: {ctx.author.voice.channel.name}"
                    )
                except Exception as e:
                    logger.error(f"Failed to connect to voice channel: {e}")
                    await ctx.send("❌ Failed to connect to the voice channel.")
                    raise commands.CommandError("Voice connection failed.") from e
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        else:
            logger.debug("Bot is already connected to a voice channel.")
