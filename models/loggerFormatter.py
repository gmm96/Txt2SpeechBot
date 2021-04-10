# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging


class CustomFormatter(logging.Formatter):
    """
    Need to add .%(msecs)03d' to every fmt str after asctime if wanna modify
    the date format and append milliseconds value
    """
    COMMON_FMT: str = "\n%(asctime)s.%(msecs)03d  |  %(levelname)s  |  File: %(filename)s, Func: %(funcName)s, Line: %(lineno)d" \
                      + "\n%(message)s\n"
    WRN_FMT: str = "%(asctime)s.%(msecs)03d  |  %(levelname)s  |  %(message)s"
    INFO_FMT: str = "%(asctime)s.%(msecs)03d  |  %(message)s"
    SP_DATE_FMT: str = "%d/%m/%Y %H:%M:%S"

    def __init__(self, fmt: str = None, date_fmt: str = None):
        fmt = fmt if fmt else CustomFormatter.COMMON_FMT
        date_fmt = date_fmt if date_fmt else CustomFormatter.SP_DATE_FMT
        super().__init__(fmt=fmt, datefmt=date_fmt, style='%')

    def format(self, record: logging.LogRecord) -> str:
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
