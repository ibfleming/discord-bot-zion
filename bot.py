import asyncio
import discord
from discord.ext import commands
from music import YTSource, music_queue
from logger import setup_logger
import music
import utils
import os
from dotenv import load_dotenv

# Setup logger
logger = setup_logger()

# Load the bot token from environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

command_lock = asyncio.Lock()


@bot.command(name="play", aliases=["p"])
async def play(ctx, *, query=None):
    if not query:
        await ctx.send(
            "> :x:   **Please provide a song name or URL to work, lil' fricker.**"
        )
        return

    async with ctx.typing():
        async with command_lock:
            if not ctx.voice_client:
                if not ctx.author.voice:
                    await ctx.send(
                        "> :x:   **You must be in a voice channel for this command to work, numbnuts.**"
                    )
                    return
                channel = ctx.author.voice.channel
                await channel.connect()

            if utils.is_url(query):
                player = await YTSource.from_url(query, loop=bot.loop, ctx=ctx)
            else:
                player = await YTSource.from_search(query, loop=bot.loop, ctx=ctx)

            if player:
                form_dur = utils.format_duration(player.data["duration"])

                if not ctx.voice_client.is_playing() and music_queue.empty():
                    ctx.voice_client.play(
                        player,
                        after=lambda e: asyncio.run_coroutine_threadsafe(
                            on_song_end(ctx), bot.loop
                        ),
                    )
                    await ctx.send(
                        f":loud_sound:   ***Now listening to:***```make\nTitle: \"{player.title}\"\nDuration: {form_dur}\nChannel: {player.data['channel']}\n```\n:musical_note:   **Enjoy the music!**   :musical_note:\n"
                    )
                else:
                    await music_queue.put(player)
                    await ctx.send(
                        f":loud_sound:   ***Added song to the queue:***```make\nTitle: \"{player.title}\"\nDuration: {form_dur}\nChannel: {player.data['channel']}\n```\n"
                    )
            else:
                await ctx.send(
                    "> :x:   **Could not fetch the video. Sorry 'bout dat.** :cry: "
                )


@bot.command(name="skip")
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("> :track_next:   **Skipping the current song, fahree.**")
        if music_queue.empty():
            await ctx.send(
                "> :wind_blowing_face:   **The queue is empty, so I'm peacin'.**"
            )
        await play_next(ctx)
    else:
        await ctx.send("> :x:   **No song is currently playing, no cap.**")


@bot.command(name="queue", aliases=["q"])
async def queue(ctx):
    if music_queue.empty():
        await ctx.send("> :x:   **The queue is empty, dummy.**")
    else:
        queue_list = "\n".join(
            [f"{i+1}. {song.title}" for i, song in enumerate(list(music_queue._queue))]
        )
        await ctx.send(f":scroll:   ***Queue:***\n```{queue_list}```")


@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


async def on_song_end(ctx):
    if ctx.voice_client:
        await play_next(ctx)


async def play_next(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        return

    if not music_queue.empty():
        player = await music_queue.get()
        form_dur = utils.format_duration(player.data["duration"])
        ctx.voice_client.play(
            player,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                on_song_end(ctx), bot.loop
            ),
        )
        await ctx.send(
            f":loud_sound:   ***Now listening to:***```make\nTitle: \"{player.title}\"\nDuration: {form_dur}\nChannel: {player.data['channel']}\n```\n:musical_note:   **Enjoy the music!**   :musical_note:\n"
        )
    else:
        await stop(ctx)


@bot.event
async def on_ready():
    logger.info("Discord bot is online and ready!")


bot.run(TOKEN, log_handler=None)
