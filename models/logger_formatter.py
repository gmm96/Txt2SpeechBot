#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging


class CustomFormatter(logging.Formatter):
    COMMON_FMT = "%(asctime)s  |  %(levelname)s  |  %(filename)s, %(funcName)s, %(lineno)d: \n%(message)s"
    WRN_FMT = "%(asctime)s  |  %(levelname)s  |  %(message)s"
    INFO_FMT = "%(asctime)s  |  %(message)s"
    DATE_FMT = "%d/%m/%Y %H:%M:%S.%f"

    def __init__(self, fmt: str = None, date_fmt: str = None):
        fmt = fmt if fmt is not None else CustomFormatter.COMMON_FMT
        date_fmt = date_fmt if date_fmt is not None else CustomFormatter.DATE_FMT
        super().__init__(fmt=fmt, datefmt=date_fmt, style='%')

    def format(self, record: logging.LogRecord) -> logging.Formatter:
        original_fmt = self._style._fmt
        if record.levelno == logging.INFO:
            self._style._fmt = CustomFormatter.INFO_FMT
        elif record.levelno == logging.WARNING:
            self._style._fmt = CustomFormatter.WRN_FMT
        elif record.levelno == logging.ERROR:
            self._style._fmt = CustomFormatter.COMMON_FMT
        result = logging.Formatter.format(self, record)
        self._style._fmt = original_fmt
        return result
