#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entry point for running the Zion Discord Bot as a module.
Usage: python -m src.bot
"""

import asyncio
import sys

from .bot import main
from .logger import logger

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot has been shut down via keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error during shutdown: {e}")
        sys.exit(1)
