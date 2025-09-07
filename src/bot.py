#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import signal

import discord
from discord.ext import commands

from .cogs.help import Help
from .cogs.music import Music
from .config import DISCORD_TOKEN
from .core.shutdown import shutdown
from .logger import logger
from .utils.terminal import configure_terminal


def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=".",
        description="Magi of Zion, the bot for Zion, dedicated for music and righteousness.",
        intents=intents,
        help_command=None,
    )

    return bot


async def main():
    configure_terminal()
    bot = create_bot()
    bot.should_exit = False

    loop = asyncio.get_running_loop()

    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(bot, s)))

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

    async with bot:
        await bot.add_cog(Help(bot))
        await bot.add_cog(Music(bot))
        try:
            await bot.start(DISCORD_TOKEN)
        except asyncio.CancelledError:
            logger.info("Bot was cancelled")
        finally:
            if not bot.is_closed():
                await bot.close()
            logger.info("Bot has been shut down gracefully")
