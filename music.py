import os
import asyncio
import discord
import yt_dlp as youtube_dl
from discord import FFmpegPCMAudio
from dotenv import load_dotenv

# Music Queue
music_queue = asyncio.Queue()

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
    "quiet": False,
    "force_ipv4": True,
    "outtmpl": "./music/%(title)s.%(ext)s",
}

fetch_opts = {
    "format": "bestaudio/best",
    "extract_flat": True,
    "quiet": False,
    "force_ipv4": True,
    "noplaylist": True,
    "outtmpl": "./music/%(title)s.%(ext)s",
}

ffmpeg_options = {"options": "-vn"}

# YoutubeDL instances
ytfetch = youtube_dl.YoutubeDL(fetch_opts)
ytdl = youtube_dl.YoutubeDL(ytdl_opts)


class YTSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, ctx=None):
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
        if "entries" in data and len(data["entries"]) > 0:
            data = data["entries"][0]
        else:
            await ctx.send("❌   No entries found in the provided URL.")
            raise Exception("No entries found in the provided URL.")

        # Ensure title and URL are available in data
        if not data or "title" not in data or "url" not in data:
            await ctx.send("❌   Video data is incomplete. Cannot process the URL.")
            raise Exception("Incomplete video data.")

        filename = f"./music/{data['title']}.mp3"
        if os.path.exists(filename):
            return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        # Download and convert audio if file doesn't exist
        try:
            await loop.run_in_executor(None, lambda: ytdl.download([url]))
        except Exception as e:
            await ctx.send(f"❌   Failed to download the video. Error: {str(e)}")
            raise Exception("Error while downloading the video.") from e

        # Ensure the file was created
        if not os.path.exists(filename):
            await ctx.send("❌   Failed to locate the downloaded file.")
            raise Exception("Downloaded file not found.")

        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_search(cls, query, *, loop=None, ctx=None):
        loop = loop or asyncio.get_event_loop()
        search_query = f"ytsearch:{query}"

        try:
            # Extract the search results
            data = await loop.run_in_executor(
                None, lambda: ytfetch.extract_info(search_query, download=False)
            )
        except Exception as e:
            await ctx.send(f"❌   Failed to fetch video data. Error: {str(e)}")
            raise Exception("Error while fetching video data.") from e

        # If it's a playlist or search result, take the first entry
        if "entries" in data and len(data["entries"]) > 0:
            data = data["entries"][0]
        else:
            await ctx.send("❌   No entries found in the provided query.")
            raise Exception("No entries found in the provided query.")

        # Ensure title and URL are available in data
        if not data or "title" not in data or "url" not in data:
            await ctx.send("❌   Video data is incomplete. Cannot process the query.")
            raise Exception("Incomplete video data.")

        filename = f"./music/{data['title']}.mp3"
        if os.path.exists(filename):
            return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        # Download and convert audio if file doesn't exist
        try:
            await loop.run_in_executor(None, lambda: ytdl.download([data["url"]]))
        except Exception as e:
            await ctx.send(f"❌   Failed to download the video. Error: {str(e)}")
            raise Exception("Error while downloading the video.") from e

        # Ensure the file was created
        if not os.path.exists(filename):
            await ctx.send("❌   Failed to locate the downloaded file.")
            raise Exception("Downloaded file not found.")

        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
