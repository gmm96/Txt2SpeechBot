# -*- coding: utf-8 -*-
# @Author: gmm96
# @Date:   2016-03-22 01:50:50
# @Last Modified by:   Guille
# @Last Modified time: 2016-09-01 03:11:36

import json
import sys
sys.path.append("/home/gmm/telegramBots/Txt2SpeechBot/")


##
## @brief  Reads a file and returns its content 
##
## @param  type     File type
## @param  file_path     Path to file
## 
## @return  The content of the specified file
##

def read_file(type, file_path):
   with open(file_path) as __file:
      if type == 'reg':
         return __file.read()
      elif type == 'json':
         # try:
         return json.load(__file)
         # except ValueError:
         #    file_backup = file_path[0:-5] + '_' + time.strftime("%d-%m-%y_%H:%M:%S") + '.json'
         #    os.system("cp " + file_path + " " + file_backup)
         #    os.system('echo "{}" > ' + file_path)
         #    bot.send_message(6216877, "Ya se ha vuelto a joder el puto json de las queries.")
         #    aux = {}
         #    return aux


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
