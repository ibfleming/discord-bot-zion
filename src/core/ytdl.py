"""YouTube download and streaming utilities for the Zion Discord Bot."""

import asyncio

import discord
import yt_dlp as youtube_dl  # type: ignore

from config import FFMPEG_OPTIONS, YTDL_FORMAT_OPTIONS

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl = youtube_dl.YoutubeDL(YTDL_FORMAT_OPTIONS)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def from_string(cls, search, *, loop=None, stream=True):
        query = f"ytsearch:{search}"
        return await cls.from_url(query, loop=loop, stream=stream)
