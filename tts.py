# -*- coding: utf-8 -*-
# @Author: gmm96
 
import os
import telebot
import requests
from telebot import types 
import sys
import pkgutil
import importlib
import urllib2
from collections import OrderedDict
from operator import itemgetter
from rfc3986 import normalize_uri
from plugins.file_processing import *
from plugins.log import *
from plugins.queries import *
from plugins.shared import *
from plugins.db import *
import subprocess
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, COMM


CALLBACK_DATA_PREFIX_FOR_PREDEFINED_AUDIOS = "audio"

reload(sys)                           # python 2
sys.setdefaultencoding("utf-8")       #



##############################################
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
    inline_results = []

    # Saving useful data
    record_uid(q.from_user)
    record_log_queries(q)

    # Personal audio
    if "" == q.query:
        sql_read = "SELECT `file_id`, `description` FROM Own_Audios WHERE id='%s'" % (str(q.from_user.id))
        result = read_db(sql_read)
        if result is not None:
            count = 1
            for audio in result:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Description", callback_data=audio[0]))
                inline_results.append(types.InlineQueryResultCachedVoice(str(count), audio[0], audio[1], reply_markup=markup))
                count += 1

    # TTS audio
    else:
        # text = urllib2.quote(text.encode('UTF-8'))
        # bot.send_message(6216877, text)
        # text = text.replace('%2B', '+')
        # bot.send_message(6216877, text)

        q.query = q.query.replace("\n", " ")
        text = normalize_uri(q.query) if isArabic(q.query) else q.query.replace(' ', '+')

        # Inline button
        code_id = store_query(q)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Text", callback_data=code_id))

        magic = TTS.format(query=text)
        cont = 1

        sql_read = "SELECT `Ar`,`De-de`,`En-uk`,`En-us`,`Es-es`,`Es-mx`,`Fr-fr`,`It-it`,`Pt-pt`,`El-gr`," + \
                   "`Ru-ru`,`Tr-tr`,`Zh-cn`,`Ja`, `Pl` FROM Lan_Results WHERE id = '%s'" % (q.from_user.id)
        result = read_db(sql_read)
        if result is not None:
            # array of (language_name, language_id, language_count)
            sorted_languages = sorted([(LAN.items()[i][0], LAN.items()[i][1], result[0][i]) for i in range(len(LAN))], key=itemgetter(2), reverse=True)
            if not isArabic(q.query):
                for i in range(len(sorted_languages)):
                    inline_results.append(types.InlineQueryResultVoice(str(cont), magic + sorted_languages[i][1], sorted_languages[i][0], reply_markup=markup))
                    cont += 1
            else:
                language_id = 0
                for i in range(len(sorted_languages)):
                    if 'Ar' in sorted_languages[i][1]:
                        language_id = i
                inline_results.append(types.InlineQueryResultVoice(str(language_id+1), magic + sorted_languages[language_id][1], sorted_languages[language_id][0], reply_markup=markup))
        else:
            if not isArabic(q.query):
                for key, val in LAN.items():
                    inline_results.append(types.InlineQueryResultVoice(str(cont), magic + val, key, reply_markup=markup))
                    cont += 1
            else:
                inline_results.append(types.InlineQueryResultVoice(str(cont), magic + LAN.items()[0][1], LAN.items()[0][0], reply_markup=markup))


    try:
        bot.answer_inline_query(q.id, inline_results, cache_time=1)
    except Exception as e:
        exc_message = str(e) + ' | query: "' + q.query + '"'
        record_exception(exc_message)
        bot.send_message(6216877, exc_message)


#######


##
## @brief  Save stats about chosen language
##
## @param  chosen_inline_result     chosen language 
##

@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def test_chosen(chosen_inline_result):
    global AUDIO_CONT

    # TTS audio
    if len(chosen_inline_result.query) > 0 and chosen_inline_result.query not in AUDIO_ID.keys():

        sql_read = "SELECT `Ar`,`De-de`,`En-uk`,`En-us`,`Es-es`,`Es-mx`,`Fr-fr`,`It-it`,`Pt-pt`,`El-gr`," + \
                   "`Ru-ru`,`Tr-tr`,`Zh-cn`,`Ja`, `Pl` FROM Lan_Results WHERE id = '%s'" % (chosen_inline_result.from_user.id)
        result = read_db(sql_read)
        if result is not None:
            sorted_languages = sorted([(LAN.items()[i][0], LAN.items()[i][1], result[0][i]) for i in range(len(LAN))], key=itemgetter(2), reverse=True)

        times = sorted_languages[int(chosen_inline_result.result_id)-1][2] + 1
        lan = sorted_languages[int(chosen_inline_result.result_id)-1][1]
        sql_update = "UPDATE Lan_Results SET `%s`='%d' WHERE id = '%s'" % (lan, times, chosen_inline_result.from_user.id)
        write_db(sql_update)

    # Personal audio
    #else:
    #    bot.send_message(6216877, str(chosen_inline_result.inline_message_id.voice))
    #    audio_id = int(chosen_inline_result.result_id)
    #    AUDIO_CONT[audio_id] = AUDIO_CONT.get(audio_id, 0) + 1
    #    write_file('pickle', 'data/audio_cont.pickle', AUDIO_CONT)


#######

##
## @brief  Define callback button to show input text
##
## @param  c     callback
##

@bot.callback_query_handler(lambda call: True)
def control_callback(c):
    global QUERIES
    sql_read = "SELECT `description` FROM Own_Audios WHERE file_id='%s'" % (c.data)
    result = read_db(sql_read)
    if result is not None:
        text = result[0][0]
    else:
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
## @brief  Defines next procedure of a step by step process.
##
## @param  m            message
## @param  text         text to send to the user
## @param  function     next procedure
##

def next_step(m, text, function):
    sendto = types.ForceReply(selective=False)
    reply = bot.reply_to(m, text, reply_markup=sendto)
    bot.register_next_step_handler(reply, function)



##
## @brief  Returns a list with all audios from user.
##
## @param  user_id      User identification number
##

def user_audio_list(user_id):
    user_dir = 'audios/' + str(user_id) + '/'
    return next(os.walk(user_dir))[2]



##
## @brief  Set of functions for the /addaudio command. Asks user for audio and stores it.
##
## @param  m   message
##

@bot.message_handler(commands=['addaudio'])
def add_audio_start(m):
    sql_read = "SELECT COUNT(`file_id`) FROM Own_Audios WHERE id='%s'" % (str(m.from_user.id))
    result = read_db(sql_read)
    if result is not None and int(result[0][0]) < 50:
        next_step(m, "Send audio or voice note.", add_audio_file)
    else:
        bot.reply_to(m, "Sorry, you reached maximun number of stored audios (50). Try removing with /rmaudio command.")

def add_audio_file(m):
    global user_focus_on
    if m.content_type == 'audio' or m.content_type == 'voice':
        user_focus_on[m.from_user.id] = m
        next_step(m, "Saved!\n\nProvide now a short description for the audio. 30 character allowed.", add_audio_description)
    else:
        bot.reply_to(m, "Audio file are not detected. Are you sure you've uploaded the correct file? Try it again with /addaudio command.")


def add_audio_description(m):
    global user_focus_on
    if m.content_type == 'text' and len(m.text) <= 30:
        sql_read = "SELECT `file_id` FROM Own_Audios WHERE id='%s' AND description='%s'" % (str(m.from_user.id), m.text.strip())
        result = read_db(sql_read)
        if result is None:
            file_message = user_focus_on[m.from_user.id]

            # Workaround to change audio to voice note
            if file_message.content_type == 'audio':
                file_link = file_message.audio
                file_info = bot.get_file(file_link.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                filename = 'audios/' + str(file_link.file_id) + ".mp3"
                try:
                    with open(filename, 'wb') as new_file:
                        new_file.write(downloaded_file)
                except EnvironmentError:
                    next_step(m, "Error writing audio. Send it again.", add_audio_file)
                subprocess.call('bash mp3_to_ogg.sh ' + filename, shell=True)
                message = bot.send_voice(6216877, open('audios/' + str(file_link.file_id) + '.ogg', 'rb'))
                os.remove('audios/' + str(file_link.file_id) + '.ogg')
                user_focus_on[m.from_user.id] = file_message = message

            file_link = file_message.voice
            sql_insert = "INSERT INTO Own_Audios(file_id, id, description, duration, size) VALUES ('%s', '%s', '%s', '%i', '%i')" % \
                            (file_link.file_id, str(m.from_user.id), m.text.strip(), file_link.duration, file_link.file_size)
            write_db(sql_insert)
            bot.reply_to(m, 'Saved audio with description: "' + m.text + '"')
        else:
            next_step(m, "Description is already in use. Please, write another one.", add_audio_description)
    else:
        next_step(m, "Wrong input. Write a short description to save the audio. 30 characters maximum.", add_audio_description)



##
## @brief  Set of functions for the /listaudio command
##
## @param  m   message
##

@bot.message_handler(commands=['listaudio'])
def list_audio(m):
    sql_statement = "SELECT `file_id`, `description`, `duration`, `size` FROM Own_Audios WHERE id='%s'" % (m.from_user.id)
    result = read_db(sql_statement)
    if result is not None:
        message = "These are your uploaded audios.\n\n"
        count = 1
        for audio in result:
            message += "%i.-  %s \t|\t %ss \t|\t %.2fKB\n" % (count, audio[1], audio[2], audio[3]/1024.0)
            count += 1
        bot.reply_to(m, message)
    else:
        bot.reply_to(m, "Sorry, you don't have any uploaded audio... Try to upload one with /addaudio command.")



##
## @brief  Set of functions for the /rmaudio command
##
## @param  m   message
##

@bot.message_handler(commands=['rmaudio'])
def rm_audio_start(m):
    list_audio(m)
    sql_statement = "SELECT `file_id`, `description` FROM Own_Audios WHERE id='%s'" % (m.from_user.id)
    result = read_db(sql_statement)
    if result is not None:
        next_step(m, "Send the description of the audio you want to remove.", rm_audio_select)



def rm_audio_select(m):
    if m.content_type == 'text':
        rm_audio_description = m.text.strip()
        sql_read = "SELECT `file_id` FROM Own_Audios WHERE id='%s' AND description='%s'" % (m.from_user.id, rm_audio_description)
        result = read_db(sql_read)
        if result is not None:
            sql_rm = "DELETE FROM Own_Audios WHERE id='%s' AND description='%s'" % (m.from_user.id, rm_audio_description)
            write_db(sql_rm)
            bot.reply_to(m, "The file was deleted from your audios.")
        else:
            bot.reply_to(m, "No audio with the provided description. Please, send the correct description. Try again /rmaudio.")
    else:
        bot.reply_to(m, "Wrong input. Send the description of the audio you want to remove. Try again /rmaudio.")



#######

##
## @brief  Regular message handler
##
## @param  m     message
##

@bot.message_handler(commands=['help'])     # python 2
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


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()
