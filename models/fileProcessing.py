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

    def read_file(self) -> Optional[Union[str, List, Tuple, Dict]]:
        try:
            with open(self.path, 'r') as __file:
                if self.file_type == LiteralConstants.FileType.REG:
                    return __file.read()
                elif self.file_type == LiteralConstants.FileType.JSON:
                    return json.load(__file)
        except Exception:
            LiteralConstants.STA_LOG.logger.exception(LiteralConstants.ExceptionMessages.FILE_CANT_OPEN, exc_info=True)
            return None

    def write_file(self, data: Union[str, List, Tuple, Dict]) -> bool:
        try:
            with open(self.path, 'w') as __file:
                if self.file_type == LiteralConstants.FileType.REG:
                    __file.write(data)
                    return True
                elif self.file_type == LiteralConstants.FileType.JSON:
                    json.dump(data, __file)
                    return True
        except Exception:
            LiteralConstants.STA_LOG.logger.exception(LiteralConstants.ExceptionMessages.FILE_CANT_WRITE, exc_info=True)
            return False
