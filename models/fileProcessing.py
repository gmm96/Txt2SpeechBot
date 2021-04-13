# !/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Optional, List, Tuple, Dict, Union
from models.literalConstants import LiteralConstants


class FileProcessing:
    BASE_PATH: str = os.getcwd() + "/"

    def __init__(self, path: str, file_type: LiteralConstants.FileType) -> None:
        self.path: str = FileProcessing.BASE_PATH + path
        self.file_type: LiteralConstants.FileType = file_type

    def read_file(self) -> Optional[Union[str, List, Tuple, Dict, bytes]]:
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

