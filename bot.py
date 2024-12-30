import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl
import re

# Load environment variables and fetch Discord token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# Youtube Downloader options
ytdl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        },
    ],
    "force_ipv4": True,
    "outtmpl": "./music/%(title)s.%(ext)s",
}

fetch_opts = {
    "format": "bestaudio/best",  # Keeps the best audio format available
    "extract_flat": True,  # Only extracts the URL and metadata, skips actual downloading
    "quiet": False,  # Suppresses unnecessary logs
    "force_ipv4": True,  # Force IPv4 to avoid possible issues with IPv6
    "noplaylist": True,  # Skip playlist extraction (if you're only fetching a single video)
    "outtmpl": "./music/%(title)s.%(ext)s",  # Adjust output template if you want
}


# FFMPEG Options
ffmpeg_options = {"options": "-vn"}

# YoutubeDL instances
fetch = youtube_dl.YoutubeDL(fetch_opts)
ytdl = youtube_dl.YoutubeDL(ytdl_opts)

# Global  queue
music_queue = asyncio.Queue()


# Classes
class YTSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, ctx):
        loop = loop or asyncio.get_event_loop()

        # Extract the search results
        data = await loop.run_in_executor(
            None,
            lambda: fetch.extract_info(
                url,
                download=False,
            ),
        )

        if "entries" in data and len(data["entries"]) > 0:
            data = data["entries"][0]
        else:
            await ctx.send("❌   No results found for the search query.")
            raise Exception("No results found for the search query.")

        # Check if the .mp3 file already exists
        filename = f"./music/{data['title']}.mp3"
        if os.path.exists(filename):
            print(f"File {filename} already exists. Skipping download.")
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        # If file doesn't exist, download and extract the audio
        await loop.run_in_executor(None, lambda: ytdl.download([url]))

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_search(cls, query, *, loop=None, ctx):
        loop = loop or asyncio.get_event_loop()
        search_query = f"ytsearch:{query}"

        # Extract the search results
        data = await loop.run_in_executor(
            None,
            lambda: fetch.extract_info(
                search_query,
                download=False,
            ),
        )

        if "entries" in data and len(data["entries"]) > 0:
            data = data["entries"][0]
        else:
            await ctx.send("❌   No results found for the search query.")
            raise Exception("No results found for the search query.")

        # Check if the .mp3 file already exists
        filename = f"./music/{data['title']}.mp3"
        if os.path.exists(filename):
            print(f"File {filename} already exists. Skipping download.")
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        # If file doesn't exist, download and extract the audio
        await loop.run_in_executor(None, lambda: ytdl.download([data["url"]]))

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def is_url(query):
    youtube_regex = (
        r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=[\w-]+|playlist\?list=[\w-]+|[a-zA-Z0-9_-]+)"
    )
    return re.match(youtube_regex, query) is not None


@bot.command(name="play")
async def play(ctx, *, query):
    async with ctx.typing():
        # Connect to the voice channel if not connected.
        if not ctx.voice_client:
            if not ctx.author.voice:
                await ctx.send(
                    "❌   You must be in a voice channel to use this command!"
                )
                return
            channel = ctx.author.voice.channel
            await channel.connect()

        # Check if query is a URL or a search query.
        if is_url(query):
            # Youtube Link
            print("Youtube Link")
            player = await YTSource.from_url(query, loop=bot.loop, ctx=ctx)
        else:
            # Youtube Search
            print("Youtube Search")
            player = await YTSource.from_search(query, loop=bot.loop, ctx=ctx)

        if player:
            # Play the song if nothing is playing and the queue is empty
            if not ctx.voice_client.is_playing() and music_queue.empty():
                ctx.voice_client.play(
                    player,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        on_song_end(ctx), bot.loop
                    ),
                )
                await ctx.send(
                    f"### Now playing: \n```Title: \"{player.title}\"\nChannel: {player.data['channel']}```"
                )
            else:
                await music_queue.put(player)
                await ctx.send(
                    f"### Added to queue: \n```Title: \"{player.title}\"\nChannel: {player.data['channel']}```"
                )
        else:
            await ctx.send("❌  Could not fetch the video.")


async def play_next(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        return  # Don't try to play next if a song is already playing

    if not music_queue.empty():
        player = await music_queue.get()  # Get the next song from the queue
        ctx.voice_client.play(
            player,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                on_song_end(ctx), bot.loop
            ),
        )
        await ctx.send(
            f"### Now playing: \n```Title: \"{player.title}\"\nChannel: {player.data['channel']}```"
        )

    else:
        # If no songs are left in the queue, disconnect
        if ctx.voice_client:  # Ensure voice_client is not None
            await ctx.send("✅  No more songs in the queue. Disconnecting...")
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("❌  Not connected to a voice channel.")


async def on_song_end(ctx):
    if ctx.voice_client:
        await play_next(ctx)


@bot.command(name="skip")
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()  # Stop the current song
        await ctx.send("⏭️  Skipped the current song. Moving to the next.")

        # Play the next song, if available
        await play_next(ctx)
    else:
        await ctx.send("❌  No song is currently playing to skip.")


@bot.command(name="queue")
async def queue(ctx):
    if music_queue.empty():
        await ctx.send("❌  The queue is empty.")
    else:
        queue_list = "\n".join(
            [f"{i+1}. {song.title}" for i, song in enumerate(list(music_queue._queue))]
        )  # Access the 'title' attribute of the YTSource object
        await ctx.send(f"### Current Queue: \n```{queue_list}```")


@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


@bot.event
async def on_ready():
    print(f"Discord bot is ready!")


bot.run(TOKEN)
