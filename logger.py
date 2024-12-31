import logging
import colorlog


def setup_logger():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.INFO)

    # Set up colorlog for colored output in the console
    handler = colorlog.StreamHandler()

    # Log format with colors
    log_format = "%(yellow)s%(asctime)s %(log_color)s%(levelname)s %(blue)s%(name)s%(white)s: %(message)s"

    formatter = colorlog.ColoredFormatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
