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
#USERS = read_file('json', 'data/users.json')
DB = read_file('json', 'data/db.json')
LAN = OrderedDict(sorted(read_file('json', 'data/languages.json').items(), key=itemgetter(0)))
# CONT = int(read_file('reg', 'data/cont.txt').rstrip())

try:
   file_path = 'data/queries.json'
   QUERIES = OrderedDict(read_file('json', file_path))
   AUDIOS = OrderedDict(sorted(read_file('json', 'data/audios.json').items(), key=itemgetter(0)))
except:
   real_time = time.strftime("%d-%m-%y_%H:%M:%S")
   file_backup = file_path[0:-5] + '_' + real_time + '.json'
   os.system("cp " + file_path + " " + file_backup)
   os.system('echo "{}" > ' + file_path)
   bot.send_message(6216877, "Ya se ha vuelto a joder el puto json de las queries a " + real_time)
   QUERIES = OrderedDict()
   

MAX_QUERIES = 100000
