# -*- coding: utf-8 -*-
# @Author: gmm96

import telebot              # API bot library
from telebot import types   # API bot types
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from plugins.file_processing import *
from plugins.shared import *
from collections import OrderedDict
import uuid



def store_query(q):
    global QUERIES
    text = q.query
    code_id = str(uuid.uuid4())
    # bot.send_message(6216877, 'queries id: ' + code_id)

    if len(QUERIES) >= MAX_QUERIES:
        QUERIES.pop(QUERIES.iterkeys().next())

    QUERIES[code_id] = text
    write_file('json', 'data/queries.json', QUERIES)
    return code_id