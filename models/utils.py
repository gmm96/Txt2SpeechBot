# -*- coding: utf-8 -*-
# @Author: gmm96

from telebot import types
import re
from models.constants import Constants
from models.database import Database
from models.file_processing import File_Processing
from operator import itemgetter
import alphabet_detector
import urllib.parse
import time, datetime
import uuid
import string
from typing import Union, Dict, List, Tuple
from rfc3986 import normalize_uri
from collections import OrderedDict


class Utils:

    def db_str ( self, text: str ) -> Union[ str, bool ]:
        if text:
            return re.sub( '[^A-Za-z0-9\s]+', '', text )
        else:
            return text or ''

    def replace_url_problematic_chars ( self, text: str ) -> str:
        text_copy = text
        for old_char, new_char in Constants.PROBLEMATIC_CHARS.items( ):
            text_copy = text_copy.replace( old_char, new_char )
        return text_copy

    def is_arabic ( self, text: str ) -> bool:
        my_ad = alphabet_detector.AlphabetDetector( )
        text_wo_digits = str(text).translate( text.maketrans( "", "", string.digits ) )
        if text_wo_digits == "":
            return False
        else:
            return my_ad.is_arabic( text_wo_digits )

    def normalize_text ( self, text: str ) -> str:
        return urllib.parse.quote( text, safe = '' )

    def store_tts_query ( self, text: str, queries: OrderedDict ) -> str:
        code_id = str( uuid.uuid4( ) )
        if len ( queries ) >= Constants.MAX_QUERIES:
            queries.pop (next(reversed(queries)))
        queries[ code_id ] = text
        return code_id

    def generate_callback_code_for_own_audios ( self ) -> str:
        return str( uuid.uuid4( ) )

    def record_message ( self, message: types.Message ) -> None:
        if message.content_type == 'text':
            if message.chat.type == Constants.ChatType.PRIVATE:
                text = str(message.from_user.username) + " (" + str( message.chat.id ) + "): " + message.text
            else:
                text = str(message.from_user.username) + '(' + str( message.from_user.id ) + ') in "' + message.chat.title + '"[' + str(
                    message.chat.id ) + ']: ' + message.text
            Constants.MSG_LOG.logger.info( datetime.datetime.now( ).strftime( "%d/%m/%y %H:%M:%S:%f" ) + " | " + text )

    def record_query ( self, query: types.InlineQuery ) -> None:
        text = str( query.from_user.username ) + " (" + str( query.from_user.id ) + "): " + query.query
        Constants.QRY_LOG.logger.info( datetime.datetime.now( ).strftime( "%d/%m/%y %H:%M:%S:%f" ) + " | " + text )

    def create_db_conn(self):
        return Database(Constants.DB_CREDENTIALS[0], Constants.DB_CREDENTIALS[1], Constants.DB_CREDENTIALS[2], Constants.DB_CREDENTIALS[3])

    def store_user ( self, user: types.User, db_conn: Database) -> None:
        sql_read = Constants.DBStatements.DB_USER_READ % (user.id)
        result = db_conn.read_one( sql_read )
        if not result:
            sql_insert_user_info = Constants.DBStatements.DB_USER_INSERT % (str(user.id), self.db_str(user.username), self.db_str(user.first_name), self.db_str(user.first_name))
            sql_insert_chosen_result = Constants.DBStatements.DB_LAN_INSERT % str(user.id)
            db_conn.write_all( sql_insert_user_info )
            db_conn.write_all( sql_insert_chosen_result )
        else:
            if not self.users_are_equal(result, user):
                sql_update = Constants.DBStatements.DB_USER_UPDATE % (self.db_str(user.username), self.db_str(user.first_name), self.db_str(user.last_name), str(user.id))
                db_conn.write_all( sql_update )

    def users_are_equal(self, user1: List, user2: types.User) -> bool:
        equals = user1[1] == str(user2.id) and user1[2] == self.db_str(user2.username) \
                 and user1[3] == self.db_str(user2.first_name) \
                 and user1[4] == self.db_str(user2.last_name)
        return equals

    def create_inline_results_personal_audio(self, q: types.InlineQuery, queries: dict, db_conn: Database) -> List[types.InlineQuery]:
        inline_results = []
        sql_read = Constants.DBStatements.DB_AUDIOS_READ_FOR_QUERY_BUILD % (str( q.from_user.id ))
        result = db_conn.read_all( sql_read )
        if len(result) > 0:
            for audio in result:
                markup = types.InlineKeyboardMarkup( )
                markup.add( types.InlineKeyboardButton("Description", callback_data=audio[3] ) )
                inline_results.append( types.InlineQueryResultCachedVoice( str(audio[2]), audio[0], audio[1], reply_markup=markup) )
        else:
            message = File_Processing('data/help.txt', Constants.FileType.REG).read_file()
            inline_results.append(
                types.InlineQueryResultArticle( 1, "No entries for personal audios",
                                                types.InputTextMessageContent( message ) ) )
            inline_results.append(
                types.InlineQueryResultArticle( 2, "You can type to get a TextToSpeech audio",
                                                types.InputTextMessageContent( message ) ) )
            inline_results.append(
                types.InlineQueryResultArticle( 3, "Or add a personal audio chatting me privately",
                                                types.InputTextMessageContent( message ) ) )
        return inline_results

    def create_inline_results_tts_audio(self, q: types.InlineQuery, queries: OrderedDict, db_conn: Database) -> List[types.InlineQuery]:
        inline_results = []
        cont = 1
        markup = types.InlineKeyboardMarkup( )
        q.query = self.replace_url_problematic_chars( q.query )
        markup.add( types.InlineKeyboardButton( "Text", callback_data=self.store_tts_query(q.query, queries) ) )
        normalized_text = normalize_uri( q.query ) if self.is_arabic( q.query ) else q.query.replace(' ', '+')
        magic = Constants.TTS_STR.format( query=normalized_text )
        iterable_lan = list(Constants.SORTED_LANGUAGES.items())

        sql_read = Constants.DBStatements.DB_LAN_READ % q.from_user.id
        result = db_conn.read_one( sql_read )
        if result is not None:
            user_sorted_lang = sorted( [ (iterable_lan[ i ][ 0 ], iterable_lan[ i ][ 1 ], result[ i ]) for i in range( len( Constants.SORTED_LANGUAGES ) ) ], key = itemgetter( 2 ), reverse = True )
            if not self.is_arabic( q.query ):
                for i in range( len( user_sorted_lang ) ):
                    inline_results.append( types.InlineQueryResultVoice( str( cont ), magic + user_sorted_lang[ i ][ 1 ], user_sorted_lang[ i ][ 0 ], reply_markup = markup ) )
                    cont += 1
            else:
                language_id = 0
                for i in range( len( user_sorted_lang ) ):
                    if 'Ar' in user_sorted_lang[ i ][ 1 ]:
                        language_id = i
                inline_results.append( types.InlineQueryResultVoice( str( language_id + 1 ), magic + user_sorted_lang[ language_id ][ 1 ], user_sorted_lang[ language_id ][ 0 ],reply_markup = markup ) )
        else:
            if not self.is_arabic( q.query ):
                for key, val in Constants.SORTED_LANGUAGES.items( ):
                    inline_results.append( types.InlineQueryResultVoice( str( cont ), magic + val, key, reply_markup = markup ) )
                    cont += 1
            else:
                inline_results.append( types.InlineQueryResultVoice( str( cont ), magic + iterable_lan[ 0 ][ 1 ], iterable_lan[ 0 ][ 0 ], reply_markup = markup ) )
        return inline_results

    def update_chosen_results_personal_audio(self, chosen_inline_result: types.ChosenInlineResult, db_conn: Database) -> None:
        sql_read = Constants.DBStatements.DB_AUDIOS_READ_FOR_CHOSEN_RESULT % (str(chosen_inline_result.from_user.id), int(chosen_inline_result.result_id))
        result = db_conn.read_one( sql_read )
        if result is not None:
            sql_update = Constants.DBStatements.DB_AUDIO_UPDATE_FOR_CHOSEN_RESULT % (result[1] + 1, result[0])
            db_conn.write_all( sql_update )

    def update_chosen_results_tts_audio(self, chosen_inline_result: types.ChosenInlineResult, db_conn: Database) -> None:
        iterable_lan = list(Constants.SORTED_LANGUAGES.items())
        sql_read = Constants.DBStatements.DB_LAN_READ % chosen_inline_result.from_user.id
        result = db_conn.read_one( sql_read )
        if result is not None:
            sorted_languages = sorted([ (iterable_lan[i][0], iterable_lan[i][1], result[i]) for i in range(len(iterable_lan)) ], key=itemgetter(2), reverse=True )
            times = sorted_languages[ int( chosen_inline_result.result_id ) - 1 ][ 2 ] + 1
            lan = sorted_languages[ int( chosen_inline_result.result_id ) - 1 ][ 1 ]
            sql_update = Constants.DBStatements.DB_LAN_UPDATE_FOR_CHOSEN_RESULT % (lan, times, chosen_inline_result.from_user.id)
            db_conn.write_all( sql_update )

    def get_callback_query(self, callback, queries: OrderedDict, db_conn: Database) -> str:
        result = db_conn.read_one( Constants.DBStatements.DB_AUDIOS_READ_FOR_CALLBACK_QUERY % callback.data )
        if result is not None:
            text = result[0]
        else:
            try:
                text = queries[callback.data]
            except KeyError:
                text = ''
        return text

    def get_free_user_audio_id ( self, taken_ids: List[int] ) -> int:
        free_ids = list(range(1, 51))
        for id in taken_ids:
            free_ids.remove( id )
        free_ids.sort( )
        return free_ids[ 0 ]

    def get_own_audios(self, user: types.User, db_conn: Database) -> Union[str, None]:
        sql_read = Constants.DBStatements.DB_AUDIOS_READ_FOR_LISTING % str(user.id)
        result = db_conn.read_all(sql_read)
        if len(result) == 0:
            return None
        else:
            message = "These are your uploaded audios.\n\n"
            count = 1
            for audio in result:
                message += "%i.-  %s \t|\t %i s \t|\t %.2fKB\n" % (count, audio[ 1 ], audio[ 2 ], audio[ 3 ] / 1024.0)
                count += 1
            return message




