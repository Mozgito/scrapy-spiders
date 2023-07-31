import logging
import os
from pathlib import Path


def mylogger(name):
    file_formatter = logging.Formatter(fmt='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                                       datefmt='%Y/%m/%d %H:%M:%S')
    console_formatter = logging.Formatter('%(levelname)s -- %(message)s')

    file_handler = logging.FileHandler(str(Path(os.path.abspath(__file__)).parent.parent.absolute()) + "/logs/log.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

    return logger
