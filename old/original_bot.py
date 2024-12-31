import asyncio
import logging
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
    "quiet": True,
    "force_ipv4": True,
    "outtmpl": "./music/%(title)s.%(ext)s",
}

fetch_opts = {
    "format": "bestaudio/best",
    "extract_flat": True,
    "quiet": True,
    "force_ipv4": True,
    "noplaylist": True,
    "outtmpl": "./music/%(title)s.%(ext)s",
}


# FFMPEG Options
ffmpeg_options = {"options": "-vn"}

# YoutubeDL instances
ytfetch = youtube_dl.YoutubeDL(fetch_opts)
ytdl = youtube_dl.YoutubeDL(ytdl_opts)

# Global  queue
music_queue = asyncio.Queue()
command_lock = asyncio.Lock()


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

        try:
            # Extract information from the URL
            data = await loop.run_in_executor(
                None, lambda: ytfetch.extract_info(url, download=False)
            )
        except Exception as e:
            await ctx.send(f"❌   Failed to fetch video data. Error: {str(e)}")
            raise Exception("Error while fetching video data.") from e

        # If it's a playlist or search result, take the first entry
        if "entries" in data:
            if len(data["entries"]) > 0:
                data = data["entries"][0]
            else:
                await ctx.send("❌   No entries found in the provided URL.")
                raise Exception("No entries found in the provided URL.")

        # Ensure title and URL are available in data
        if not data or "title" not in data or "url" not in data:
            await ctx.send("❌   Video data is incomplete. Cannot process the URL.")
            raise Exception("Incomplete video data.")

        # Check if the .mp3 file already exists
        filename = f"./music/{data['title']}.mp3"
        if os.path.exists(filename):
            print(f"File {filename} already exists. Skipping download.")
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        # Download and convert audio if file doesn't exist
        try:
            print(f"Downloading audio for {data['title']}...")
            await loop.run_in_executor(None, lambda: ytdl.download([url]))
        except Exception as e:
            await ctx.send(f"❌   Failed to download the video. Error: {str(e)}")
            raise Exception("Error while downloading the video.") from e

        # Ensure the file was created
        if not os.path.exists(filename):
            await ctx.send("❌   Failed to locate the downloaded file.")
            raise Exception("Downloaded file not found.")

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_search(cls, query, *, loop=None, ctx):
        loop = loop or asyncio.get_event_loop()
        search_query = f"ytsearch:{query}"

        try:
            # Extract the search results
            data = await loop.run_in_executor(
                None,
                lambda: ytfetch.extract_info(
                    search_query,
                    download=False,
                ),
            )
        except Exception as e:
            await ctx.send(f"❌   Failed to fetch video data. Error: {str(e)}")
            raise Exception("Error while fetching video data.") from e

        # If it's a playlist or search result, take the first entry
        if "entries" in data:
            if len(data["entries"]) > 0:
                data = data["entries"][0]
            else:
                await ctx.send("❌   No entries found in the provided URL.")
                raise Exception("No entries found in the provided URL.")

        # Ensure title and URL are available in data
        if not data or "title" not in data or "url" not in data:
            await ctx.send("❌   Video data is incomplete. Cannot process the URL.")
            raise Exception("Incomplete video data.")

        # Check if the .mp3 file already exists
        filename = f"./music/{data['title']}.mp3"
        if os.path.exists(filename):
            print(f"File {filename} already exists. Skipping download.")
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        # Download and convert audio if file doesn't exist
        try:
            print(f"Downloading audio for {data['title']}...")
            await loop.run_in_executor(None, lambda: ytdl.download([data["url"]]))
        except Exception as e:
            await ctx.send(f"❌   Failed to download the video. Error: {str(e)}")
            raise Exception("Error while downloading the video.") from e

        # Ensure the file was created
        if not os.path.exists(filename):
            await ctx.send("❌   Failed to locate the downloaded file.")
            raise Exception("Downloaded file not found.")

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def is_url(query):
    youtube_regex = (
        r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=[\w-]+|playlist\?list=[\w-]+|[a-zA-Z0-9_-]+)"
    )
    return re.match(youtube_regex, query) is not None


@bot.command(name="play", aliases=["p"])
async def play(ctx, *, query=None):
    if not query:
        await ctx.send("❌   Please provide a song name or URL to play!")
        return

    async with ctx.typing():
        async with command_lock:
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
                # print("Youtube Link")
                player = await YTSource.from_url(query, loop=bot.loop, ctx=ctx)
            else:
                # Youtube Search
                # print("Youtube Search")
                player = await YTSource.from_search(query, loop=bot.loop, ctx=ctx)

            if player:
                duration = player.data["duration"]
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                formatted_duration = f"{minutes}m {seconds}s"
                # Play the song if nothing is playing and the queue is empty
                if not ctx.voice_client.is_playing() and music_queue.empty():
                    ctx.voice_client.play(
                        player,
                        after=lambda e: asyncio.run_coroutine_threadsafe(
                            on_song_end(ctx), bot.loop
                        ),
                    )
                    await ctx.send(
                        f"### Now playing: \n```Title: \"{player.title}\"\nChannel: {player.data['channel']}\nDuration: {formatted_duration}```"
                    )
                else:
                    await music_queue.put(player)
                    await ctx.send(
                        f"### Added to the queue: \n```Title: \"{player.title}\"\nChannel: {player.data['channel']}\nDuration: {formatted_duration}```"
                    )
            else:
                await ctx.send("❌   Could not fetch the video.")


async def play_next(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        return  # Don't try to play next if a song is already playing

    if not music_queue.empty():
        player = await music_queue.get()  # Get the next song from the queue
        duration = player.data["duration"]
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        formatted_duration = f"{minutes}m {seconds}s"
        ctx.voice_client.play(
            player,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                on_song_end(ctx), bot.loop
            ),
        )
        await ctx.send(
            f"### Now playing: \n```Title: \"{player.title}\"\nChannel: {player.data['channel']}\nDuration: {formatted_duration}```"
        )

    else:
        # If no songs are left in the queue, disconnect
        if ctx.voice_client:  # Ensure voice_client is not None
            await ctx.send("✅   No more songs in the queue. Disconnecting...")
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("❌   Not connected to a voice channel.")


async def on_song_end(ctx):
    if ctx.voice_client:
        await play_next(ctx)


@bot.command(name="skip")
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()  # Stop the current song
        await ctx.send("⏭️   Skipped the current song. Moving to the next.")

        # Play the next song, if available
        await play_next(ctx)
    else:
        await ctx.send("❌   No song is currently playing to skip.")


@bot.command(name="queue", aliases=["q"])
async def queue(ctx):
    if music_queue.empty():
        await ctx.send("❌   The queue is empty.")
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


bot.run(TOKEN, log_handler=None)
