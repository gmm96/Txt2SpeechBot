# !/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import alphabet_detector
import urllib.parse
import uuid
import string
from telebot import types
from operator import itemgetter
from rfc3986 import normalize_uri
from collections import OrderedDict
from typing import Union, List, Tuple, Optional
from models.constants import Constants
from models.database import Database
from models.fileProcessing import FileProcessing


class Utils:

    @staticmethod
    def db_str(text: str) -> str:
        if text:
            return re.sub('[^A-Za-z0-9\s]+', '', text)
        else:
            return text or ''

    @staticmethod
    def replace_url_problematic_chars(text: str) -> str:
        text_copy = text
        for old_char, new_char in Constants.PROBLEMATIC_CHARS.items():
            text_copy = text_copy.replace(old_char, new_char)
        return text_copy

    @staticmethod
    def is_arabic(text: str) -> bool:
        my_ad = alphabet_detector.AlphabetDetector()
        text_wo_digits = str(text).translate(text.maketrans("", "", string.digits))
        if text_wo_digits == "":
            return False
        else:
            return my_ad.is_arabic(text_wo_digits)

    @staticmethod
    def normalize_text(text: str) -> str:
        return urllib.parse.quote(text, safe='')

    @staticmethod
    def store_tts_query(text: str, queries: OrderedDict) -> str:
        code_id = str(uuid.uuid4())
        if len(queries) >= Constants.MAX_QUERIES:
            queries.pop(next(reversed(queries)))
        queries[code_id] = text
        return code_id

    @staticmethod
    def generate_callback_code_for_own_audios() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def record_message(message: types.Message) -> None:
        if message.content_type == 'text':
            if message.chat.type == Constants.ChatType.PRIVATE:
                text = str(message.from_user.username) + " (" + str(message.chat.id) + "): " + message.text
            else:
                text = str(message.from_user.username) + '(' + str(message.from_user.id) + ') in "' + \
                       message.chat.title + '"[' + str(message.chat.id) + ']: ' + message.text
            Constants.MSG_LOG.logger.info(text)

    @staticmethod
    def record_query(query: types.InlineQuery) -> None:
        text = str(query.from_user.username) + " (" + str(query.from_user.id) + "): " + query.query
        Constants.QRY_LOG.logger.info(text)

    @staticmethod
    def create_db_conn() -> Database:
        return Database(Constants.DB_CREDENTIALS[0], Constants.DB_CREDENTIALS[1],
                        Constants.DB_CREDENTIALS[2], Constants.DB_CREDENTIALS[3])

    @staticmethod
    def store_user(user: types.User, db_conn: Database) -> None:
        sql_read = Constants.DBStatements.DB_USER_READ % str(user.id)
        result = db_conn.read_one(sql_read)
        if not result:
            sql_insert_user_info = Constants.DBStatements.DB_USER_INSERT % (str(user.id), Utils.db_str(user.username),
                                                                            Utils.db_str(user.first_name),
                                                                            Utils.db_str(user.first_name))
            sql_insert_chosen_result = Constants.DBStatements.DB_LAN_INSERT % str(user.id)
            db_conn.write_all(sql_insert_user_info)
            db_conn.write_all(sql_insert_chosen_result)
        else:
            if not Utils.users_are_equal(result, user):
                sql_update = Constants.DBStatements.DB_USER_UPDATE % (Utils.db_str(user.username),
                                                                      Utils.db_str(user.first_name),
                                                                      Utils.db_str(user.last_name), str(user.id))
                db_conn.write_all(sql_update)

    @staticmethod
    def users_are_equal(user1: Tuple, user2: types.User) -> bool:
        equals = user1[1] == str(user2.id) and \
                 user1[2] == Utils.db_str(user2.username) and \
                 user1[3] == Utils.db_str(user2.first_name) and \
                 user1[4] == Utils.db_str(user2.last_name)
        return equals

    @staticmethod
    def create_inline_results_personal_audio(q: types.InlineQuery, db_conn: Database) \
            -> List[Union[types.InlineQueryResultCachedVoice, types.InlineQueryResultArticle]]:
        inline_results = []
        sql_read = Constants.DBStatements.DB_AUDIOS_READ_FOR_QUERY_BUILD % str(q.from_user.id)
        result = db_conn.read_all(sql_read)
        if len(result) > 0:
            for audio in result:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Description", callback_data=audio[3]))
                inline_results.append(types.InlineQueryResultCachedVoice(
                    str(audio[2]), audio[0], audio[1], reply_markup=markup
                ))
        else:
            message = FileProcessing('data/help.txt', Constants.FileType.REG).read_file()
            inline_results.append(types.InlineQueryResultArticle(
                1, "No entries for personal audios", types.InputTextMessageContent(message)
            ))
            inline_results.append(types.InlineQueryResultArticle(
                2, "You can type to get a TextToSpeech audio", types.InputTextMessageContent(message)
            ))
            inline_results.append(types.InlineQueryResultArticle(
                3, "Or add a personal audio chatting me privately", types.InputTextMessageContent(message)
            ))
        return inline_results

    @staticmethod
    def create_inline_results_tts_audio(q: types.InlineQuery, queries: OrderedDict,
                                        db_conn: Database) -> List[types.InlineQueryResultVoice]:
        inline_results = []
        cont = 1
        markup = types.InlineKeyboardMarkup()
        q.query = Utils.replace_url_problematic_chars(q.query)
        markup.add(types.InlineKeyboardButton("Text", callback_data=Utils.store_tts_query(q.query, queries)))
        normalized_text = normalize_uri(q.query) if Utils.is_arabic(q.query) else q.query.replace(' ', '+')
        magic = Constants.TTS_STR.format(query=normalized_text)
        iterable_lan = list(Constants.SORTED_LANGUAGES.items())

        sql_read = Constants.DBStatements.DB_LAN_READ % str(q.from_user.id)
        result = db_conn.read_one(sql_read)
        if result is not None:
            user_sorted_lang = sorted(
                [(iterable_lan[i][0], iterable_lan[i][1], result[i]) for i in range(len(Constants.SORTED_LANGUAGES))],
                key=itemgetter(2), reverse=True
            )
            if not Utils.is_arabic(q.query):
                for i in range(len(user_sorted_lang)):
                    inline_results.append(types.InlineQueryResultVoice(
                        str(cont), magic + user_sorted_lang[i][1], user_sorted_lang[i][0], reply_markup=markup
                    ))
                    cont += 1
            else:
                language_id = 0
                for i in range(len(user_sorted_lang)):
                    if 'Ar' in user_sorted_lang[i][1]:
                        language_id = i
                inline_results.append(types.InlineQueryResultVoice(
                    str(language_id + 1), magic + user_sorted_lang[language_id][1],
                    user_sorted_lang[language_id][0], reply_markup=markup
                ))
        else:
            if not Utils.is_arabic(q.query):
                for key, val in Constants.SORTED_LANGUAGES.items():
                    inline_results.append(types.InlineQueryResultVoice(
                        str(cont), magic + val, key, reply_markup=markup
                    ))
                    cont += 1
            else:
                inline_results.append(types.InlineQueryResultVoice(
                    str(cont), magic + iterable_lan[0][1], iterable_lan[0][0], reply_markup=markup
                ))
        return inline_results

    @staticmethod
    def update_chosen_results_personal_audio(chosen_inline_result: types.ChosenInlineResult, db_conn: Database) -> None:
        sql_read = Constants.DBStatements.DB_AUDIOS_READ_FOR_CHOSEN_RESULT % \
                   (str(chosen_inline_result.from_user.id), int(chosen_inline_result.result_id))
        result = db_conn.read_one(sql_read)
        if result:
            sql_update = Constants.DBStatements.DB_AUDIO_UPDATE_FOR_CHOSEN_RESULT % (result[1] + 1, result[0])
            db_conn.write_all(sql_update)

    @staticmethod
    def update_chosen_results_tts_audio(chosen_inline_result: types.ChosenInlineResult, db_conn: Database) -> None:
        iterable_lan = list(Constants.SORTED_LANGUAGES.items())
        sql_read = Constants.DBStatements.DB_LAN_READ % chosen_inline_result.from_user.id
        result = db_conn.read_one(sql_read)
        if result is not None:
            sorted_languages = sorted(
                [(iterable_lan[i][0], iterable_lan[i][1], result[i]) for i in range(len(iterable_lan))],
                key=itemgetter(2), reverse=True
            )
            times = sorted_languages[int(chosen_inline_result.result_id) - 1][2] + 1
            lan = sorted_languages[int(chosen_inline_result.result_id) - 1][1]
            sql_update = Constants.DBStatements.DB_LAN_UPDATE_FOR_CHOSEN_RESULT % (lan, times,
                                                                                   chosen_inline_result.from_user.id)
            db_conn.write_all(sql_update)

    @staticmethod
    def get_callback_query(callback, queries: OrderedDict, db_conn: Database) -> str:
        result = db_conn.read_one(Constants.DBStatements.DB_AUDIOS_READ_FOR_CALLBACK_QUERY % callback.data)
        if result is not None:
            text = result[0]
        else:
            try:
                text = queries[callback.data]
            except KeyError:
                text = ''
        return text

    @staticmethod
    def get_free_user_audio_id(taken_ids: List[int]) -> int:
        free_ids = list(range(1, 51))
        for audio_id in taken_ids:
            free_ids.remove(audio_id)
        free_ids.sort()
        return free_ids[0]

    @staticmethod
    def get_own_audios(user: types.User, db_conn: Database) -> Optional[str]:
        sql_read = Constants.DBStatements.DB_AUDIOS_READ_FOR_LISTING % str(user.id)
        result = db_conn.read_all(sql_read)
        if len(result) == 0:
            return None
        else:
            message = "These are your uploaded audios.\n\n"
            count = 1
            for audio in result:
                message += "%i.-  %s \t|\t %i s \t|\t %.2fKB\n" % (count, audio[1], audio[2], audio[3] / 1024.0)
                count += 1
            return message

    @staticmethod
    def is_file_voice(msg: types.Message) -> bool:
        return msg.content_type == 'voice'

    @staticmethod
    def is_document_media_file(msg: types.Message) -> bool:
        if msg.content_type == 'document':
            file_type = msg.document.mime_type.split('/')[0]
            if file_type in Constants.CONTENT_TYPE:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def is_file_media(msg: types.Message) -> bool:
        return msg.content_type in Constants.CONTENT_TYPE or Utils.is_document_media_file(msg)

    @staticmethod
    def should_convert_to_voice(msg: types.Message) -> bool:
        return msg.content_type == 'audio' or msg.content_type == 'video' or Utils.is_document_media_file(msg)
