from logging import Logger, StreamHandler, Formatter
import logging
import os

loggingLevel = logging.INFO

logger: dict[str,Logger] = dict()

def getLogger(name: str = None, prefix: str = "", level = None) -> Logger:
    global loggingLevel
    level = level if level is not None else loggingLevel

    if name is None:
        name = str(os.getpid())

    if name in logger:
        return logger[name]

    logFormatter = Formatter(fmt=f"{prefix}[%(levelname)s]: %(message)s")

    # create console handler
    consoleHandler = StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(level)

    logger[name] = logging.getLogger(name)
    logger[name].setLevel(level)
    logger[name].addHandler(consoleHandler)

    return logger[name]


def setLoggingLevel(debug: bool, quiet: int):
    global loggingLevel
    if debug:
        loggingLevel = logging.DEBUG
        return loggingLevel
    
    if quiet == 1:
        loggingLevel = logging.WARNING
    elif quiet == 2:
        loggingLevel = logging.ERROR
    elif quiet == 3:
        loggingLevel = logging.CRITICAL

    return loggingLevel
