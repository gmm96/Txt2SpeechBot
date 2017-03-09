# -*- coding: utf-8 -*-
# @Author: gmm96
 
import telebot
import requests
from telebot import types 
import sys
import pkgutil
import importlib
import urllib
from collections import OrderedDict
from operator import itemgetter
from plugins.file_processing import *
from plugins.log import *
from plugins.queries import *
from plugins.shared import * 

reload(sys)                           # python 2
sys.setdefaultencoding("utf-8")       #


#############################################
## Listener

##
## @brief  Receives all messages that bot listens and records important info
##
## @param  messages     list of messages
##
def listener(messages): 
    for m in messages:
        record_uid(m.from_user)   # Record user id
        record_log_messages(m)   # Log file



## Declare last function as bot's listener
bot.set_update_listener(listener)

#################################################

##
## @brief  Inline message handler
##
## @param  q     query (inline message request)
##

@bot.inline_handler(lambda query: 0 <= len(query.query) <= 201)
def query_handler(q):
    global QUERIES

    # Saving useful data
    record_uid(q.from_user)
    record_log_queries(q)

    # Parsing url
    text = q.query.replace(' ', '+')

    # Query for callback
    code_id = store_query(q)

    # bot.send_message(6216877, 'query id: ' + code_id)

    # Inline button
    b1 = types.InlineKeyboardButton("Text", callback_data=code_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(b1)
    inline_results = []

    # Predifined audio menu
    if "" == q.query or "menu" == q.query:
        cont = 1
        for txt,url in AUDIOS.items():
            inline_results.append(types.InlineQueryResultVoice(str(cont), url, txt.capitalize()))
            cont += 1

    # Predifined audio selection
    elif q.query in AUDIOS:
        inline_results.append(types.InlineQueryResultVoice(str(1), AUDIOS[q.query], q.query.capitalize(), reply_markup=markup))

    # Regular audio
    else:
        url = TTS.format(query=text)
        cont = 1

        sql_read = "SELECT `Ar`,`De-de`,`En-uk`,`En-us`,`Es-es`,`Es-mx`,`Fr-fr`,`It-it`,`Pt-pt`,`El-gr`," + \
                   "`Ru-ru`,`Zh-cn`,`Ja` FROM chosen_results WHERE id = '%s'" % (q.from_user.id)
        result = read_db(sql_read)
        if result is not None:
            sorted_languages = sorted([(LAN.items()[i][0], LAN.items()[i][1], result[0][i]) for i in range(len(LAN))], key=itemgetter(2), reverse=True)
            for i in range(len(sorted_languages)):
                inline_results.append(types.InlineQueryResultVoice(str(cont), url + sorted_languages[i][1], sorted_languages[i][0], reply_markup=markup))
                cont += 1
        else:
            for key, val in LAN.items():
                inline_results.append(types.InlineQueryResultVoice(str(cont), url + val, key, reply_markup=markup))
                cont += 1


    bot.answer_inline_query(q.id, inline_results, cache_time=1)



#######


##
## @brief  Save stats about chosen language
##
## @param  chosen_inline_result     chosen language
##

@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def test_chosen(chosen_inline_result):
    if len(chosen_inline_result.query) > 0:

        sql_read = "SELECT `Ar`,`De-de`,`En-uk`,`En-us`,`Es-es`,`Es-mx`,`Fr-fr`,`It-it`,`Pt-pt`,`El-gr`," + \
                   "`Ru-ru`,`Zh-cn`,`Ja` FROM chosen_results WHERE id = '%s'" % (chosen_inline_result.from_user.id)
        result = read_db(sql_read)
        if result is not None:
            sorted_languages = sorted([(LAN.items()[i][0], LAN.items()[i][1], result[0][i]) for i in range(len(LAN))], key=itemgetter(2), reverse=True)

        times = sorted_languages[int(chosen_inline_result.result_id)-1][2] + 1
        lan = sorted_languages[int(chosen_inline_result.result_id)-1][1]
        sql_update = "UPDATE chosen_results SET `%s`='%d' WHERE id = '%s'" % (lan, times, chosen_inline_result.from_user.id)
        update_db(sql_update)


#######

##
## @brief  Define callback button to show input text
##
## @param  c     callback
##

@bot.callback_query_handler(lambda call: True)
def control_callback(c):
    global QUERIES
    try:
        text = QUERIES[c.data]
    except KeyError:
        text = ''
    
    if len(text) > 54:      
        bot.answer_callback_query(c.id, text, show_alert=True)
    else:
        bot.answer_callback_query(c.id, text)


#######

##
## @brief  Regular message handler
##
## @param  m     message
##

@bot.message_handler(func=lambda msg:msg.text.encode("utf-8"))     # python 2
# @bot.message_handler(content_types=['text'])                     # python 3
def commands(m):
    message = read_file('reg', 'data/message.txt')
    bot.send_message(m.from_user.id, message)



#############################################
## Requests

## Continue working even if there are errors
#bot.skip_pending = True
#bot.polling(none_stop=True)
while True:
    try:
        bot.polling(none_stop=True)
    except requests.exceptions.ConnectionError as e:
        print >> sys.stderr, str(e)
        time.sleep(15)
