# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing FileProcessing class.
"""

import json
from typing import Optional, List, Tuple, Dict, Union
from pathlib import Path
from helpers.literalConstants import LiteralConstants


class FileProcessing:
    """
    Python class to read and write from files in filesystem.

    This is just a simple class to perform read and write actions in files in disk. It has support
    for regular files as txt, json files and raw files so you can get the bytes of them. File
    descriptor won't be generated in instance creation, so a new one will be created every time you
    make an operation.
    """

    BASE_PATH: str = str(Path(__file__).parent.parent.parent.resolve()) + "/"
    """ Path to the root project directory. """

    def __init__(self, path: str, file_type: LiteralConstants.FileType) -> None:
        """
        Opens a file to perform operations on it.

        :param path: Path to filename.
        :param file_type: REG or JSON or BYTES.
        """
        self.path: str = FileProcessing.BASE_PATH + path
        self.file_type: LiteralConstants.FileType = file_type

    def read_file(self) -> Optional[Union[str, List, Tuple, Dict, bytes]]:
        """
        Reads the content of a specified file in the filesystem and returns it.

        :return: Content taken from the file.
        :rtype: Str or list or tuple or dict or bytes or None.
        """
        try:
            file = open(self.path, 'r') if self.file_type != LiteralConstants.FileType.BYTES else open(self.path, 'rb')
            if self.file_type == LiteralConstants.FileType.REG or self.file_type == LiteralConstants.FileType.BYTES:
                return file.read()
            elif self.file_type == LiteralConstants.FileType.JSON:
                return json.load(file)
        except EnvironmentError:
            LiteralConstants.STA_LOG.logger.exception(LiteralConstants.ExceptionMessages.FILE_CANT_OPEN, exc_info=True)
            return None
        else:
            file.close()

    def write_file(self, data: Union[str, List, Tuple, Dict]) -> bool:
        """
        Writes the given data into a specified file of filesystem and returns the result of the
        operation.

        :param data: Data to be written into the file.
        :return: True if write operation is ok, False otherwise.
        :rtype: Bool.
        """
        try:
            file = open(self.path, 'w') if self.file_type != LiteralConstants.FileType.BYTES else open(self.path, 'wb')
            if self.file_type == LiteralConstants.FileType.REG or self.file_type == LiteralConstants.FileType.BYTES:
                file.write(data)
                return True
            elif self.file_type == LiteralConstants.FileType.JSON:
                json.dump(data, file)
                return True
        except EnvironmentError:
            LiteralConstants.STA_LOG.logger.exception(LiteralConstants.ExceptionMessages.FILE_CANT_WRITE, exc_info=True)
            return False
        else:
            file.close()
