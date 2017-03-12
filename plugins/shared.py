# -*- coding: utf-8 -*-
# @Author: gmm96

import telebot              # API bot library
from telebot import types   # API bot types
from plugins.file_processing import *
from collections import OrderedDict
from operator import itemgetter
import os
import time


############## Creates bot object ###############
TOKEN = read_file('reg', 'data/token.txt').rstrip()
bot = telebot.TeleBot(TOKEN)

############### Global variables ################
DB = read_file('json', 'data/db.json')
LAN = OrderedDict(sorted(read_file('json', 'data/languages.json').items(), key=itemgetter(0)))
TTS = read_file('reg', 'data/magic.txt')
AUDIO_URL = OrderedDict(sorted(read_file('json', 'data/audio_url.json').items(), key=itemgetter(0)))
AUDIO_ID = read_file('json', 'data/audio_id.json')
AUDIO_ID_REVERSED = dict(((v, k) for k, v in AUDIO_ID.items()))
AUDIO_CONT = read_file('json', 'data/audio_cont.json')

try:
    file_path = 'data/queries.json'
    QUERIES = OrderedDict(read_file('json', file_path))
except:
    real_time = time.strftime("%d-%m-%y_%H:%M:%S")
    file_backup = file_path[0:-5] + '_' + real_time + '.json'
    os.rename(file_path, file_backup)
    with open(file_path, "w") as f:
       f.write("{}")
    bot.send_message(6216877, "Ya se ha vuelto a joder el puto json de las queries a " + real_time)
    QUERIES = OrderedDict()

MAX_QUERIES = 100000
