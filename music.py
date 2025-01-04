import os
import asyncio
import discord
from requests import delete
import yt_dlp as youtube_dl
from discord import FFmpegPCMAudio
from logger import logger
import spotify
import utils

# Music Queue
music_queue = asyncio.Queue()

# Youtube Fetch options
fetch_opts = {
    "format": "bestaudio/best",
    "extract_flat": True,
    "quiet": True,
    "force_ipv4": True,
    "noplaylist": False,
    "outtmpl": "./music/%(title)s.%(ext)s",
}

ffmpeg_options = {"options": "-vn"}

# YoutubeDL instances
ytfetch = youtube_dl.YoutubeDL(fetch_opts)


class MusicSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_query(cls, query, *, loop=None, ctx=None):
        loop = loop or asyncio.get_event_loop()

        try:
            # Determine if the query is a URL or a search term
            if utils.is_yt_url(query):  # Is youtube link?
                data = await loop.run_in_executor(
                    None, lambda: ytfetch.extract_info(query, download=False)
                )
            elif utils.utils.is_spotify_url(query):  # Is spotify track?
                search_query = f"ytsearch:{spotify.spotify_url_to_yt_search(query)}"
                logger.info(f"Spotify search query: {search_query}")
                data = await loop.run_in_executor(
                    None, lambda: ytfetch.extract_info(search_query, download=False)
                )
            else:  # Treat it as a search query (for Youtube)
                search_query = f"ytsearch:{query}"
                data = await loop.run_in_executor(
                    None, lambda: ytfetch.extract_info(search_query, download=False)
                )
        except Exception as e:
            await ctx.send(f"❌   Failed to fetch video data. Error: {str(e)}")
            raise Exception("Error while fetching video data.") from e

        # If the data contains multiple entries (playlist or search result), select the first one
        if "entries" in data and len(data["entries"]) > 0:
            data = data["entries"][0]
        elif "title" in data and "url" in data:  # If it's a single video
            pass
        else:
            await ctx.send("❌   No entries found.")
            raise Exception("No entries found.")

        # Ensure title and URL are available in data
        if not data or "title" not in data or "url" not in data:
            await ctx.send("❌   Video data is incomplete. Cannot process the query.")
            raise Exception("Incomplete video data.")

        # Sanitize only the filename
        sanitized_name = utils.sanitize_filename(data["title"])  # Sanitize title only
        filename = os.path.join("./music", f"{sanitized_name}.mp3")

        if os.path.exists(filename):
            logger.info("File is already downloaded. Playing the file.")
            return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        # Download and convert audio if file doesn't exist
        logger.info(
            "File has not been downloaded before. Trying to download and play the file."
        )
        try:
            # Prepare yt-dlp options for output filename
            output_template = os.path.join("./music", f"{sanitized_name}.%(ext)s")
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
                "outtmpl": output_template,
            }
            ytdl = youtube_dl.YoutubeDL(ytdl_opts)
            # If the query is a URL, download it directly. Otherwise, download the first result from the search.
            url_to_download = query if utils.is_yt_url(query) else data["url"]
            await loop.run_in_executor(None, lambda: ytdl.download([url_to_download]))
        except Exception as e:
            await ctx.send(f"❌   Failed to download the video. Error: {str(e)}")
            raise Exception("Error while downloading the video.") from e

        # Ensure the file was created
        if not os.path.exists(filename):
            await ctx.send("❌   Failed to locate the downloaded file.")
            raise Exception("Downloaded file not found.")

        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
