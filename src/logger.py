# logger.py

import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="<fg #494948>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</fg #494948> <fg #1D85CC>{module}.{function}:{line}</fg #1D85CC> <level>[{level}] {message}</level>",
    level="INFO",
)
