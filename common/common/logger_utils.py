import logging
import os
from logging.handlers import RotatingFileHandler

# 5 MB
_MAX_LOG_SIZE = 5 * 1024 * 1024

_DIRECTORY = os.environ.get('LOGS_DIRECTORY', '.')


def setup_logger(plugin_name) -> logging.Logger:
    log_handler = RotatingFileHandler(
        filename=f'{_DIRECTORY}/{plugin_name}.log',
        mode='a',
        maxBytes=_MAX_LOG_SIZE,
        backupCount=0,
        encoding=None
    )

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            log_handler,
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(plugin_name)
    logger.setLevel(logging.DEBUG)

    return logger
