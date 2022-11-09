# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing Logger class.
"""

import logging
import os
import sys
from helpers.loggerFormatter import LoggerFormatter


class Logger:
    """
    Custom logger class to automatize the process of application logging

    The main purpose of this class is to set up a channel to logging file in disk. It also provides
    the option to display the messages in the standard output, as well as a custom formatter based
    on logging level, so every message type has a proper way to be displayed. You can access the
    logging object by parameter logger.
    """

    BASE_PATH: str = os.getcwd() + "/"
    """ Root project directory path. """

    def __init__(self, name: str, file: str, level: int = logging.INFO) -> None:
        """
        Creates a logger channel ready to record different actions.

        :param name: Name of the logger.
        :param file: Path to logger file in disk.
        :param level: Sets the threshold of the logger, defaults to logging.INFO.
        """
        self.filename: str = Logger.BASE_PATH + file
        self.name: str = name
        self.level: int = level
        self.handler: logging.FileHandler = logging.FileHandler(self.filename)
        self.handler.setFormatter(LoggerFormatter())
        self.logger: logging.Logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        self.logger.addHandler(self.handler)

    def log_also_to_stdout(self) -> None:
        """
        Add a channel to the logger to display its messages also in standard output.
        """
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
