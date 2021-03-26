#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Optional, List, Tuple, Dict, Union
from models.literal_constants import Literal_Constants


class File_Processing:
    BASE_PATH = os.getcwd( ) + "/"

    def __init__ ( self, path: str, type: Literal_Constants.FileType ) -> None:
        self.path: str = File_Processing.BASE_PATH + path
        self.type: str = type

    def read_file ( self ) -> Optional[Union[str, Dict[str, str]]]:
        try:
            with open( self.path, 'r' ) as __file:
                if self.type == Literal_Constants.FileType.REG:
                    return __file.read( )
                elif self.type == Literal_Constants.FileType.JSON:
                    return json.load( __file )
        except Exception as e:
            exc_info = Literal_Constants.ExceptionMessages.FILE_CANT_OPEN + str(e)
            Literal_Constants.STATUS_LOG.logger.exception(exc_info)
            print(exc_info)
            return None

    def write_file ( self, data: Union[str, Dict[str, str]] ) -> bool:
        try:
            with open( self.path, 'w' ) as __file:
                if self.type == Literal_Constants.FileType.REG:
                    __file.write( data )
                    return True
                elif self.type == Literal_Constants.FileType.JSON:
                    json.dump( data, __file )
                    return True
        except Exception as e:
            exc_info = Literal_Constants.ExceptionMessages.FILE_CANT_WRITE + str(e)
            Literal_Constants.STATUS_LOG.logger.exception(exc_info)
            print(exc_info)
            return False
