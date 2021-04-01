# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from models.loggerFormatter import CustomFormatter


class Logger:
    BASE_PATH: str = os.getcwd() + "/"

    def __init__(self, name: str, file: str, level: int = logging.INFO):
        self.filename: str = Logger.BASE_PATH + file
        self.name: str = name
        self.level: int = level
        self.handler: logging.FileHandler = logging.FileHandler(self.filename)
        self.handler.setFormatter(CustomFormatter())
        self.logger: logging.Logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        self.logger.addHandler(self.handler)

    def log_also_to_stdout(self) -> None:
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
