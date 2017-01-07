# -*- coding: utf-8 -*-
# @Author: gmm96
# @Date:   2016-07-14 20:13:40
# @Last Modified by:   gmm96
# @Last Modified time: 2016-07-16 21:24:12

import telebot              # API bot library
from telebot import types   # API bot types
import sys 
sys.path.append("/home/gmm/telegramBots/Txt2SpeechBot/")
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