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
import subprocess
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

    # Saving useful data
    record_uid(q.from_user)
    record_log_queries(q)

    q.query = q.query.replace("\n", " ")
    text = normalize_uri(q.query) if isArabic(q.query) else q.query.replace(' ', '+')

    # Query for callback
    code_id = store_query(q)

    # bot.send_message(6216877, 'query id: ' + code_id)

    # Inline button
    b1 = types.InlineKeyboardButton("Text", callback_data=code_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(b1)
    inline_results = []

    # text = urllib2.quote(text.encode('UTF-8'))
    # bot.send_message(6216877, text)
    # text = text.replace('%2B', '+')
    # bot.send_message(6216877, text)


    # Predifined audio menu
    if "" == q.query:
        for txt,url in AUDIO_URL.items():
            audio_id = AUDIO_ID[txt]
            b1 = types.InlineKeyboardButton("Text", callback_data=CALLBACK_DATA_PREFIX_FOR_PREDEFINED_AUDIOS + str(audio_id))
            markup = types.InlineKeyboardMarkup()
            markup.add(b1)
            inline_results.append(types.InlineQueryResultVoice(str(audio_id), url, txt.capitalize(), reply_markup=markup))

    # Predifined audio selection
    #elif q.query in AUDIO_URL:
    #    inline_results.append(types.InlineQueryResultVoice(str(AUDIO_ID[q.query]), AUDIO_URL[q.query], q.query.capitalize(), reply_markup=markup))

    # Regular audio
    else:
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

    # Regular audio
    if len(chosen_inline_result.query) > 0 and chosen_inline_result.query not in AUDIO_ID.keys():

        sql_read = "SELECT `Ar`,`De-de`,`En-uk`,`En-us`,`Es-es`,`Es-mx`,`Fr-fr`,`It-it`,`Pt-pt`,`El-gr`," + \
                   "`Ru-ru`,`Tr-tr`,`Zh-cn`,`Ja`, `Pl` FROM Lan_Results WHERE id = '%s'" % (chosen_inline_result.from_user.id)
        result = read_db(sql_read)
        if result is not None:
            sorted_languages = sorted([(LAN.items()[i][0], LAN.items()[i][1], result[0][i]) for i in range(len(LAN))], key=itemgetter(2), reverse=True)

        times = sorted_languages[int(chosen_inline_result.result_id)-1][2] + 1
        lan = sorted_languages[int(chosen_inline_result.result_id)-1][1]
        sql_update = "UPDATE Lan_Results SET `%s`='%d' WHERE id = '%s'" % (lan, times, chosen_inline_result.from_user.id)

        update_db(sql_update)

    # Predifined audio
    else:
        audio_id = int(chosen_inline_result.result_id)
        AUDIO_CONT[audio_id] = AUDIO_CONT.get(audio_id, 0) + 1
        write_file('pickle', 'data/audio_cont.pickle', AUDIO_CONT)


#######

##
## @brief  Define callback button to show input text
##
## @param  c     callback
##

@bot.callback_query_handler(lambda call: True)
def control_callback(c):
    global QUERIES
    text = ''
    if c.data.startswith(CALLBACK_DATA_PREFIX_FOR_PREDEFINED_AUDIOS):
        audio_id = c.data[len(CALLBACK_DATA_PREFIX_FOR_PREDEFINED_AUDIOS):]
        if audio_id.isdigit():
            audio_id = int(audio_id)
            if audio_id in AUDIO_ID_REVERSED:
                text = AUDIO_ID_REVERSED[audio_id].capitalize()
    if not text:
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
    #sql_statement = "SELECT COUNT(`filename`) FROM Own_Audios WHERE id='%s'" % (m.from_user.id)
    #result = read_db(sql_statement)
    #if result is None or len(result) < 20:

    if len(user_audio_list(m.from_user.id)) < 20:
        next_step(m, "Send audio or voice note.\n\t- Format: telegram voice note (.ogg) or .mp3\n\t- Size limit: 128Kb", add_audio_file)
    else:
        bot.reply_to(m, "Maximum number of audio files reached!")


def add_audio_file(m):
    global user_focus_on
    if m.content_type == 'audio' or m.content_type == 'voice':

        file_link = m.audio if m.content_type == 'audio' else m.voice
        bot.send_message(m.from_user.id, str(file_link.file_size) + file_link.mime_type + str(file_link.duration))
        allowed_mime_types = ["audio/mpeg", "audio/ogg", "audio/x-opus+ogg"]
        if file_link.file_size <= 524288 and file_link.mime_type in allowed_mime_types:

            file_info = bot.get_file(file_link.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            dir_path = "audios/" + str(m.from_user.id) + "/"
            filename = str(file_link.file_id) + ".ogg"
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            try:
                with open(dir_path + filename, 'wb') as new_file:
                    new_file.write(downloaded_file)
                    if file_link.mime_type == 'audio/mpeg':
                        subprocess.call("mp3_to_ogg.sh " + dir_path + filename, shell=True)
                    bot.reply_to(m, "Saved!")
                    user_focus_on[m.from_user.id] = filename
                    next_step(m, "Provide now a short description for the audio. 30 character allowed.", add_audio_description)
            except EnvironmentError:
                next_step(m, "Error writing audio. Send it again.", add_audio_file)

        else:
            next_step(m, "Audio file size exceed limit. Limit is 128Kb. Try with other audio.", add_audio_file)
    else:
        next_step(m, "Audio file are not detected. Are you sure you've uploaded the correct file? Try it again.", add_audio_file)


def add_audio_description(m):
    global user_focus_on
    if m.content_type == 'text' and len(m.text) <= 30:
        filename = 'audios/' + str(m.from_user.id) + '/' + user_focus_on[m.from_user.id]
        #file_size = os.path.getsize(filename)
        #duration = int(subprocess.check_output('bash get_duration.sh %s' % (filename), shell=True).rstrip())
        #sql_statement = "INSERT INTO Own_Audios(filename, id, description, duration, size) VALUES ('%s', '%s', '%s', '%i', '%i')" % \
        #                (user_focus_on[m.from_user.id], str(m.from_user.id), m.text, duration, file_size)
        #insert_db(sql_statement)
        try:
            tags = ID3(filename)
        except ID3NoHeaderError:
            tags = ID3()
        tags["COMM"] = COMM(encoding=3, lang=u'eng', desc='desc', text=m.text.decode('utf-8'))
        tags.save(filename)
        bot.reply_to(m, "Saved audio with description: " + m.text)
    else:
        next_step(m, "Wrong input. Write a short description to save the audio. 30 characters maximum.", add_audio_description)



##
## @brief  Set of functions for the /listaudio command
##
## @param  m   message
##

@bot.message_handler(commands=['listaudio'])
def list_audio(m):
    #sql_statement = "SELECT `filename`, `description`, `duration`, `size` FROM Own_Audios WHERE id='%s'" % (m.from_user.id)
    #result = read_db(sql_statement)
    #if result is not None and len(result) > 0:
    #    message = "These are your uploaded audios:\n"
    #    for audio in result:
    #        message += "%i.-\t %s \t-\t %s:%s s,\t %.2f KB\n" % (, audio[1], minutes, seconds, audio_size)

    audios = user_audio_list(m.from_user.id)
    if len(audios) != 0:
        message = "These are your uploaded audios:\n"
        count = 0
        audio_list = {}
        for audio in audios:
            audio_list[count] = audio
            tags = ID3(user_dir + audio)
            audio_comment = tags[u'COMM:desc:eng'].text[0].encode('utf-8')
            audio_length = subprocess.check_output("ffmpeg -i " + user_dir + audio + " 2>&1 | grep Duration | awk '{print $2}' | tr -d ,", shell=True).decode('utf-8').rstrip().split(':')
            minutes, seconds = audio_length[0], audio_length[1]
            audio_size = os.path.getsize(user_dir + audio) / 1024.0
            message += "%i.-\t %s \t-\t %s:%s s,\t %.2f KB\n" % (count, audio_comment, minutes, seconds, audio_size)
            count += 1
        bot.reply_to(m, message)
        return audio_list
    else:
        bot.reply_to(m, "Sorry, you don't have any uploaded audio... Try to upload one with /addaudio command.")



##
## @brief  Set of functions for the /rmaudio command
##
## @param  m   message
##

@bot.message_handler(commands=['rmaudio'])
def rm_audio_start(m):
    audios = user_audio_list(m.from_user.id)
    if len(audios) != 0:
        audio_list = list_audio(m)
        next_step(m, "Send the digit of the audio you want to remove.", rm_audio_select)
    else:
        bot.reply_to(m, "Sorry, you don't have uploaded any audio. Try it with /addaudio command.")



def rm_audio_select(m):
    if m.content_type != 'text' and m.text.isdigit() and int(m.text):
        m = m.text


#######

##
## @brief  Regular message handler
##
## @param  m     message
##

@bot.message_handler(func=lambda message: True, content_types=['text'])     # python 2
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
