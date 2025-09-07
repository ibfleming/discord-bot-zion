"""Graceful shutdown procedures for the program."""

from logger import logger


async def shutdown(bot, sig):
    logger.info(f"Received exit signal {sig.name}...")

    for vc in list(bot.voice_clients):
        try:
            await vc.disconnect(force=True)
            logger.info(f"Disconnected from voice channel {vc.channel}")
        except Exception as e:
            logger.error(f"Error disconnecting from voice channel: {e}")

    if not bot.is_closed():
        try:
            await bot.close()
            logger.info("Successfully closed bot connection")
        except Exception as e:
            logger.error(f"Error closing bot connection: {e}")

    bot.should_exit = True
