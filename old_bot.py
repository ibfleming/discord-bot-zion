import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl
from collections import deque

# Load environment variables and fetch Discord token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# Fetch Metadata Options
meta_ytdl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "extract_flat": False,
    "force_generic_extractor": True,
}

# Youtube Downloader options
audio_ytdl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        },
    ],
    "force_ipv4": True,
}

# FFMPEG Options
ffmpeg_options = {"options": "-vn"}

# YoutubeDL instances
meta_ytdl = youtube_dl.YoutubeDL(meta_ytdl_opts)
audio_ytdl = youtube_dl.YoutubeDL(audio_ytdl_opts)

# Global variables for the queue and state
music_queue = deque()  # More efficient queue with deque
IS_PLAYING = False


class YoutubeSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: audio_ytdl.extract_info(url, download=True)
        )
        if "entries" in data:
            data = data["entries"][0]
        filename = data["url"]  # URL for the audio stream
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_search(cls, query, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        search_query = f"ytsearch:{query}"
        data = await loop.run_in_executor(
            None, lambda: audio_ytdl.extract_info(search_query, download=True)
        )
        if "entries" in data and len(data["entries"]) > 0:
            data = data["entries"][0]
        filename = data["url"]  # URL for the audio stream
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def is_youtube_url(query):
    return query.startswith(
        (
            "http://www.youtube.com/",
            "https://www.youtube.com/",
            "http://youtu.be/",
            "https://youtu.be/",
        )
    )


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


@bot.command()
async def play(ctx, *, query):
    global IS_PLAYING, music_queue

    # Connect to the voice channel is not connected.
    if not ctx.voice_client:
        if not ctx.author.voice:
            await ctx.send("❌   You must be in a voice channel to use this command!")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    # If Youtube URL
    if is_youtube_url(query):
        if not IS_PLAYING:
            IS_PLAYING = True
            player = await YoutubeSource.from_url(query, loop=bot.loop)
            if player:
                ctx.voice_client.play(
                    player,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        on_song_end(ctx), bot.loop
                    ),
                )
                await ctx.send(f"### Now playing: \n```{player.title}```")
        else:
            music_queue.append({"url": query})
            await ctx.send(f'🎵   Added to the queue: "{query}"')
    # If Not URL
    else:
        if not IS_PLAYING:
            IS_PLAYING = True
            player = await YoutubeSource.from_search(query, loop=bot.loop)
            if player:
                ctx.voice_client.play(
                    player,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        on_song_end(ctx), bot.loop
                    ),
                )
                await ctx.send(f"### Now playing: \n```{player.title}```")
        else:
            music_queue.append({"url": query})
            await ctx.send(f'🎵   Added to the queue: "{query}"')


async def play_next(ctx):
    global IS_PLAYING, music_queue

    if not music_queue:
        IS_PLAYING = False
        await ctx.send("✅   The queue is empty. Leaving...")
        await ctx.voice_client.disconnect()
        return

    song = music_queue.popleft()  # Pop the next song from the queue

    if is_youtube_url(song["url"]):
        player = await YoutubeSource.from_url(song["url"], loop=bot.loop)
        if player:
            ctx.voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    on_song_end(ctx), bot.loop
                ),
            )
            await ctx.send(f"### Now playing: \n```{player.title}```")
        else:
            await ctx.send("❌   Failed to fetch the video.")
            await play_next(ctx)
    else:
        player = await YoutubeSource.from_search(song["url"], loop=bot.loop)
        if player:
            ctx.voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    on_song_end(ctx), bot.loop
                ),
            )
            await ctx.send(f"### Now playing: \n```{player.title}```")
        else:
            await ctx.send("❌   Failed to fetch the video.")
            await play_next(ctx)


async def on_song_end(ctx):
    global IS_PLAYING
    IS_PLAYING = False
    await play_next(ctx)


@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️   Skipped the current song.")
    else:
        await ctx.send("❌   No song is currently playing.")


@bot.command()
async def queue(ctx):
    if not music_queue:
        await ctx.send("❌   The queue is empty.")
    else:
        queue_list = "\n".join(
            [f"{i+1}. {q['url']}" for i, q in enumerate(music_queue)]
        )
        await ctx.send(f"🎶   Current Queue:\n{queue_list}")


bot.run(TOKEN)
