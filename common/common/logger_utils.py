import logging
from logging.handlers import RotatingFileHandler

# 5 MB
_MAX_LOG_SIZE = 5 * 1024 * 1024


def setup_logger():
    log_handler = RotatingFileHandler(
        filename='current.log',
        mode='a',
        maxBytes=_MAX_LOG_SIZE,
        backupCount=2,
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
