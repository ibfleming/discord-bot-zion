import asyncio
import discord
from discord.ext import commands
from logger import logger
from music import MusicSource
import utils
import os
from dotenv import load_dotenv


# Load the bot token from environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

command_lock = asyncio.Lock()

bot_channel = None
bot_voice = None
music_queue = asyncio.Queue()


@bot.command(name="play", aliases=["p"])
async def play(ctx, *, query=None):
    global bot_channel, bot_voice, music_queue

    # Check for arguments
    if not query:
        await ctx.send(
            "> :x:   **Please provide a song name or URL to work, lil' fricker.**"
        )
        return

    # Main logic
    async with ctx.typing():
        async with command_lock:

            # Check if connected to voice channel
            if bot_voice is None:
                # If user is not in a channel
                if ctx.author.voice is None:
                    await ctx.send(
                        "> :x:   **You must be in a voice channel for this command to work, numbnuts.**"
                    )
                    return
                else:
                    await ctx.author.voice.channel.connect()
                    bot_voice = ctx.voice_client
                    bot_channel = bot_voice.channel
                    if bot_voice and bot_channel is None:
                        logger.info(
                            f"Failed to connect to '{ctx.author.voice.channel.name}'."
                        )
                        return
                    logger.info(
                        f"Successfully connected to '{ctx.author.voice.channel.name}'."
                    )

            # Should be connected to a voice channel at this point!
            # Check if the user's channel and bot's current channel match!
            if bot_channel != ctx.author.voice.channel:
                await ctx.send(
                    "> :x:   **The bot is already in another channel, kick rocks cuzzo.**"
                )
                return
            else:
                logger.info(f"Bot is currently connected to '{bot_channel.name}'.")
                # We are connected here, if the bot isn't playing music and queue is empty.
                if not bot_voice.is_playing() and music_queue.empty():
                    logger.info(f"Bot isn't playing music and the queue is empty.")
                    player = await MusicSource.from_query(query, loop=bot.loop, ctx=ctx)
                    if player:
                        form_dur = utils.format_duration(player.data["duration"])
                        await ctx.send(
                            f":loud_sound:   ***Now listening to:***```make\nTitle: \"{player.title}\"\nDuration: {form_dur}\nChannel: {player.data['channel']}\n```\n:musical_note:   **Enjoy the music!**   :musical_note:\n"
                        )
                        bot_voice.play(
                            player,
                            after=lambda e: asyncio.run_coroutine_threadsafe(
                                on_song_end(ctx), bot.loop
                            ),
                        )
                else:
                    # We are already playing music and the queue is not empty
                    logger.info(
                        "Bot is already playing music. Trying to add it to the queue."
                    )
                    player = await MusicSource.from_query(query, loop=bot.loop, ctx=ctx)
                    if player:
                        form_dur = utils.format_duration(player.data["duration"])
                        await ctx.send(
                            f":loud_sound:   ***Added song to the queue:***```make\nTitle: \"{player.title}\"\nDuration: {form_dur}\nChannel: {player.data['channel']}\n```\n"
                        )
                        await music_queue.put(player)
                        logger.info("Added the song to the queue successfully.")


@bot.command(name="skip")
async def skip(ctx):
    global bot_voice, music_queue
    if bot_voice and bot_voice.is_playing():
        bot_voice.stop()
        await ctx.send("> :track_next:   **Skipping the current song, fahree.**")
        await play_next(ctx)
    else:
        await ctx.send("> :x:   **No song is currently playing, no cap.**")


@bot.command(name="queue", aliases=["q"])
async def queue(ctx):
    global music_queue
    if music_queue.empty():
        await ctx.send("> :x:   **The queue is empty, dummy.**")
    else:
        queue_list = "\n".join(
            [f"{i+1}. {song.title}" for i, song in enumerate(list(music_queue._queue))]
        )
        await ctx.send(f":scroll:   ***Queue:***\n```{queue_list}```")


@bot.command(name="stop")
async def stop(ctx):
    global bot_channel, bot_voice, music_queue
    if bot_voice:
        await bot_voice.disconnect()
        # Set the globals to None and clear the music queue
        bot_channel = None
        bot_voice = None
        while not music_queue.empty():
            music_queue.get_nowait()


async def on_song_end(ctx):
    global bot_voice
    if bot_voice:
        await play_next(ctx)


async def play_next(ctx):
    if bot_voice and bot_voice.is_playing():
        return

    if not music_queue.empty():
        player = await music_queue.get()
        form_dur = utils.format_duration(player.data["duration"])
        bot_voice.play(
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
