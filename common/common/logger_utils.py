import logging
from logging.handlers import RotatingFileHandler
import sys
from types import TracebackType
from typing import Type, Any

# 5 MB
_MAX_LOG_SIZE = 5 * 1024 * 1024


def my_except_hook(exctype: Type[BaseException], value: BaseException, traceback: TracebackType | None) -> Any:
    logging.critical(value, exc_info=True)
    sys.__excepthook__(exctype, value, traceback)


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
    sys.excepthook = my_except_hook
