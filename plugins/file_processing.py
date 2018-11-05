# -*- coding: utf-8 -*-
# @Author: gmm96

import json
import sys
import os
import cPickle as pickle

sys.path.append(os.path.dirname(os.getcwd()))


##
## @brief  Reads a file and returns its content 
##
## @param  type     File type
## @param  file_path     Path to file
## 
## @return  The content of the specified file
##

def read_file(type, file_path):
    with open(file_path, 'r') as __file:
        if type == 'reg':
            return __file.read()
        elif type == 'json':
            return json.load(__file)
        elif type == 'pickle':
            try:
                return pickle.load(__file)
            except EOFError:
                return {}



##
## @brief  Write some info in file
##
## @param  type     File type
## @param  file_path     Path to file
## @param  info_to_save     Info to save in file
##

def write_file(type, file_path, info_to_save):
    with open(file_path, 'w') as __file:
        if type == 'reg':
            __file.write(info_to_save)
        elif type == 'json':
            json.dump(info_to_save, __file)
        elif type == 'pickle':
            pickle.dump(info_to_save, __file)
