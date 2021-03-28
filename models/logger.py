#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from models.logger_formatter import CustomFormatter


class Logger:
    BASE_PATH = os.getcwd( ) + "/"

    def __init__ ( self, name: str, file: str, level: int = logging.INFO ):
        self.filename = Logger.BASE_PATH + file
        self.name = name
        self.level = level
        self.handler = logging.FileHandler( self.filename )
        self.handler.setFormatter( CustomFormatter() )
        self.logger = logging.getLogger( self.name )
        self.logger.setLevel( self.level )
        self.logger.addHandler( self.handler )

    def log_also_to_stdout(self):
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
