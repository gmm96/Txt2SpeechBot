# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing LoggerFormatter class.
"""

import logging


class LoggerFormatter(logging.Formatter):
    """
    Custom formatter class for logging purposes.

    This class allows us to set up different messages for every level of the logger object, this is
    why format method is overridden. We can also modify the date format of the logging object, so
    it can work with every localization. Formats are attached to the class as class fields.

    Need to add .%(msecs)03d' to every format str after asctime if wanna modify the date format and
    append milliseconds value
    """

    COMMON_FMT: str = "\n%(asctime)s.%(msecs)03d  |  %(levelname)s  |  " + \
                      "File: %(filename)s, Func: %(funcName)s, Line: %(lineno)d" + \
                      "\n%(message)s\n"
    """Common format used for every logging message except next exceptions."""

    WRN_FMT: str = "%(asctime)s.%(msecs)03d  |  %(levelname)s  |  %(message)s"
    """Format to be displayed in warning messages."""

    INFO_FMT: str = "%(asctime)s.%(msecs)03d  |  %(message)s"
    """Format to be displayed in information messages."""

    SP_DATE_FMT: str = "%d/%m/%Y %H:%M:%S"
    """Date format in Spanish."""

    def __init__(self, fmt: str = None, date_fmt: str = None) -> None:
        """
        Creates a custom formatter for a logging object.

        :param fmt: Common format to be displayed. If no value, COMMON_FMT value is set.
        :param date_fmt: Date format to be displayed in messages. If no value, SP_DATE_FMT value is set.
        """
        fmt = fmt if fmt else LoggerFormatter.COMMON_FMT
        date_fmt = date_fmt if date_fmt else LoggerFormatter.SP_DATE_FMT
        super().__init__(fmt=fmt, datefmt=date_fmt, style='%')

    def format(self, record: logging.LogRecord) -> str:
        """
        Sets a different format for every logging level.

        :param record: Message to record in the logger.
        :return: Formatted message.
        :rtype: Str.
        """
        original_fmt = self._style._fmt
        if record.levelno == logging.INFO:
            self._style._fmt = LoggerFormatter.INFO_FMT
        elif record.levelno == logging.WARNING:
            self._style._fmt = LoggerFormatter.WRN_FMT
        elif record.levelno == logging.ERROR:
            self._style._fmt = LoggerFormatter.COMMON_FMT
        result = logging.Formatter.format(self, record)
        self._style._fmt = original_fmt
        return result
