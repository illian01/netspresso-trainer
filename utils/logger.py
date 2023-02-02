import logging
import time

__all__ = ['set_logger']

def _custom_logger(name):
    fmt = f'[%(levelname)s][%(filename)s:%(lineno)s][%(funcName)s] %(asctime)s >>> %(message)s'
    fmt_date = '%Y-%m-%d_%T %Z'
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()

        formatter = logging.Formatter(fmt, fmt_date)
        handler.setFormatter(formatter)

        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    return logger

def set_logger(logger_name, level):
    try:
        time.tzset()
    except AttributeError as e:
        print(e)
        print("Skipping timezone setting.")
    _custom_logger(name=logger_name)
    logger = logging.getLogger(logger_name)
    _level = level.upper()
    if _level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif _level == 'INFO':
        logger.setLevel(logging.INFO)
    elif _level == 'WARNING':
        logger.setLevel(logging.WARNING)
    elif _level == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif _level == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
    return logger

if __name__ == '__main__':
    set_logger(__name__, level='DEBUG')