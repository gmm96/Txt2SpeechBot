# -*- coding: utf-8 -*-
# @Author: gmm96
# @Date:   2016-03-13 00:16:58
# @Last Modified by:   gmm96
# @Last Modified time: 2016-07-17 16:17:11


import telebot              # API bot library
from telebot import types   # API bot types
import sys 
sys.path.append("/home/gmm/telegramBots/Txt2SpeechBot/")
from plugins.file_processing import *
from plugins.shared import *
from plugins.db import *
import time



##
## @brief  Records id of users who message around the bot
##
## @param  m     message object
##

def record_uid_messages(m):
    sql_read = "SELECT * FROM user_info WHERE id = '%s'" % (m.from_user.id)
    result = read_db(sql_read)
    if result is None:
        sql_insert = "INSERT INTO user_info(id, username, first_name, last_name) VALUES ('%s', '%s', '%s', '%s')" % \
                      (m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
        insert_db(sql_insert)
    else:
        result = result[0]
        up_to_date = result[1]==m.from_user.id and result[2]==m.from_user.username and \
                     result[3]==m.from_user.first_name and result[4]==m.from_user.last_name
        if not up_to_date:
            sql_update = "UPDATE user_info SET username='%s', first_name='%s', last_name='%s' WHERE id = '%s'" % \
                         (m.from_user.username, m.from_user.first_name, m.from_user.last_name, m.from_user.id)
            update_db(sql_update)


##
## @brief  Saves bot around activity in log file
##
## @param  m     message object
##

def record_log_messages(m):
   if m.content_type == 'text':
      message = time.strftime("%d/%m/%y %H:%M:%S") + " | " 
      if m.chat.id > 0:                                            # Conversación privada
         message += str(user_name(m.from_user)) + " (" + str(m.chat.id) + "): " + m.text
      else:                                                        # Grupos
         message += user_name(m.from_user) + '(' + str(m.from_user.id) + ') in "' + m.chat.title + '"[' + str(m.chat.id) + ']: ' + m.text

      print(message)
      with open('log.txt', 'a') as __log:
         __log.write(message + "\n")



##
## @brief  Records id of users who query the bot
##
## @param  q     query object
##

def record_uid_queries(q):
    sql_read = "SELECT * FROM user_info WHERE id = '%s'" % (q.from_user.id)
    result = read_db(sql_read)
    if result is None:
        sql_insert = "INSERT INTO user_info(id, username, first_name, last_name) VALUES ('%s', '%s', '%s', '%s')" % \
                      (q.from_user.id, q.from_user.username, q.from_user.first_name, q.from_user.last_name)
        insert_db(sql_insert)
    else:
        result = result[0]
        up_to_date = result[1]==q.from_user.id and result[2]==q.from_user.username and \
                     result[3]==q.from_user.first_name and result[4]==q.from_user.last_name
        if not up_to_date:
            sql_update = "UPDATE user_info SET username='%s', first_name='%s', last_name='%s' WHERE id = '%s'" % \
                         (q.from_user.username, q.from_user.first_name, q.from_user.last_name, q.from_user.id)
            update_db(sql_update)



##
## @brief  Saves bot queries in log file
##
## @param  q     query object
##

def record_log_queries(q):
    query = time.strftime("%d/%m/%y %H:%M:%S") + " | " + str(user_name(q.from_user)) + " (" + str(q.from_user.id) + "): " + q.query
    print(query)
    with open('log.txt', 'a') as __log:
        __log.write(query + "\n")



##
## @brief  Records an exception in log file
##
## @param  em     exception message
##

def record_exception(em):
   with open('log.txt', 'a') as __log:
      __log.write(em + '\n')


##
## @brief  Returns the username
##
## @param  user     user object
##
## @return  Username if available, full name otherwise
##
def user_name(user):
    return user.username  