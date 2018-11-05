# -*- coding: utf-8 -*-
# @Author: gmm96


import telebot  # API bot library
from telebot import types  # API bot types
import sys
import os

sys.path.append(os.path.dirname(os.getcwd()))
from plugins.file_processing import *
from plugins.shared import *
from plugins.db import *
import time
import re


##
## @brief  Records id of users who use the bot
##
## @param  user     user object
##

def record_uid(user):
    sql_read = "SELECT * FROM User_Info WHERE id = '%s'" % (user.id)

    result = read_db(sql_read)
    if result is None:
        sql_insert_user_info = "INSERT INTO User_Info(id, username, first_name, last_name) VALUES ('%s', '%s', '%s', '%s')" % \
                               (user.id, user.username, rm_special_char(user.first_name),
                                rm_special_char(user.last_name))
        insert_db(sql_insert_user_info)

        sql_insert_chosen_result = "INSERT INTO Lan_Results(id) VALUES('%s')" % (user.id)
        insert_db(sql_insert_chosen_result)
    else:
        result = result[0]
        up_to_date = result[1] == user.id and result[2] == user.username and \
                     result[3] == user.first_name and result[4] == user.last_name
        if not up_to_date:
            sql_update = "UPDATE User_Info SET username='%s', first_name='%s', last_name='%s' WHERE id = '%s'" % \
                         (user.username, rm_special_char(user.first_name), rm_special_char(user.last_name), user.id)
            update_db(sql_update)


##
## @brief  Saves message activity in log file
##
## @param  m     message object
##

def record_log_messages(m):
    if m.content_type == 'text':
        message = time.strftime("%d/%m/%y %H:%M:%S") + " | "
        if m.chat.id > 0:  # private chat
            message += str(user_name(m.from_user)) + " (" + str(m.chat.id) + "): " + m.text
        else:  # group chat
            message += user_name(m.from_user) + '(' + str(m.from_user.id) + ') in "' + m.chat.title + '"[' + str(
                m.chat.id) + ']: ' + m.text

        print(message)
        with open('log.txt', 'a') as __log:
            __log.write(message + "\n")


##
## @brief  Saves bot queries in log file
##
## @param  q     query object
##

def record_log_queries(q):
    query = time.strftime("%d/%m/%y %H:%M:%S") + " | " + str(user_name(q.from_user)) + " (" + str(
        q.from_user.id) + "): " + q.query
    print(query)
    with open('log.txt', 'a') as __log:
        __log.write(query + "\n")


##
## @brief  Removes emojis and special characters from string
##
## @param  string
##

def rm_special_char(string):
    if string is not None:
        return re.sub('[^A-Za-z0-9\s]+', '', string)
    else:
        return string


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
