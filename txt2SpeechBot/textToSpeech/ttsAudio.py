# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing TTSAudio class.
"""

import re
import urllib.parse
from telebot import types
from collections import OrderedDict
from typing import List, Optional, Tuple
from helpers.constants import Constants
from helpers.utils import Utils
from textToSpeech.language import Language


class TTSAudio:
    """
    Python class to manipulate a cached text to speech audio.

    This class could be considered as a set of utilities to deal and create cached audios in
    Telegram system by a text to speech approach. It main purpose it's to deal with inline queries,
    chosen inline queries and callback queries, but it also has auxiliary methods that complements
    its business logic, as some tools to check the x based on the type of characters
    attached to the Telegram message.
    """

    REGEX_JAPANESE: str = "[\u3040-\u30ff]"
    """Regex to find Japanese characters."""
    REGEX_CHINESE: str = "[\u4e00-\u9FFF]"
    """Regex to find Chinese characters."""
    REGEX_KOREAN: str = "[\uac00-\ud7a3]"
    """Regex to find Korean characters."""
    REGEX_ARABIC: str = "[\u0600-\u06ff]|[\u0750-\u077f]|[\ufb50-\ufbc1]|[\ufbd3-\ufd3f]|" + \
                        "[\ufd50-\ufd8f]|[\ufd92-\ufdc7]|[\ufe70-\ufefc]|[\uFDF0-\uFDFD]"
    """Regex to find Arabic characters."""

    @staticmethod
    def create_inline_results_tts_audio(query: types.InlineQuery, queries: OrderedDict
                                        ) -> List[types.InlineQueryResultVoice]:
        """
        Creates and returns inline results for a user to answer an inline query about text to
        speech audios.

        :param query: Telegram inline query.
        :param queries: Dictionary that contains all created callbacks.
        :return: Inline results to answer a query.
        :rtype: List [types.InlineQueryResultVoice].
        """
        db_conn = Utils.create_db_conn()
        markup = types.InlineKeyboardMarkup()
        magic = TTSAudio.generate_voice_content(query.query)
        markup.add(types.InlineKeyboardButton("Text", callback_data=TTSAudio.store_tts_query(query.query, queries)))
        sql_read = Constants.DBStatements.LAN_READ % str(query.from_user.id)
        result = db_conn.read_one(sql_read)
        if result:
            return TTSAudio.__create_inline_results_with_db_entry(query.query, magic, markup, result)
        else:
            return TTSAudio.__create_inline_results_without_db_entry(query.query, magic, markup)

    @staticmethod
    def __create_inline_results_without_db_entry(query: str, magic: str, markup: types.InlineKeyboardMarkup,
                                                 ) -> List[types.InlineQueryResultVoice]:
        """
        Returns inline results for an user without previous records in database.

        :param query: String used in the query.
        :param magic: String used to point the queries.
        :param markup: Button attached to the audio to get its description.
        :return: Inline results to answer a query.
        :rtype: List[types.InlineQueryResultVoice].
        """
        languages = Language.get_languages_sorted_alphabetically()
        return TTSAudio.__build_all_inline_results(query, languages, magic, markup)

    @staticmethod
    def __create_inline_results_with_db_entry(query: str, magic: str, markup: types.InlineKeyboardMarkup,
                                              db_result: Tuple[int]) -> List[types.InlineQueryResultVoice]:
        """
        Returns inline results for an user with previous records in database.

        :param query: String used in the query.
        :param magic: String used to point the queries.
        :param markup: Button attached to the audio to get its description.
        :param db_result: Tuple that contains the number of times a user utilized every x.
        :return: Inline results to answer a query.
        :rtype: List[types.InlineQueryResultVoice].
        """
        user_sorted_lang = Language.get_languages_sorted_for_user(db_result)
        return TTSAudio.__build_all_inline_results(query, user_sorted_lang, magic, markup)

    @staticmethod
    def __build_all_inline_results(query: str, languages: List[Language], magic: str,
                                   markup: types.InlineKeyboardMarkup) -> List[types.InlineQueryResultVoice]:
        """
        Builds and returns all possible inline results for a certain query.

        :param query: Query to be processed.
        :param languages: List of sorted Languages.
        :param magic: String used to point queries.
        :param markup: Inline keyboard markup.
        :return: List of inline results.
        :rtype: List[types.InlineQueryResultVoice].
        """
        inline_results = []
        if TTSAudio.is_arabic(query):
            inline_results.append(TTSAudio.__build_language_inline_result(languages, 'Ar', magic, markup))
        elif TTSAudio.is_cjk(query):
            cjk_langs = list(filter(lambda x: x.code == 'Ja' or x.code == 'Zh-cn', languages))
            for lang in cjk_langs:
                inline_results.append(TTSAudio.__build_language_inline_result(languages, lang.code, magic, markup))
        else:
            for index, language in enumerate(languages):
                inline_results.append(types.InlineQueryResultVoice(
                    str(index + 1),
                    magic + language.code,
                    language.title,
                    reply_markup=markup
                ))
        return inline_results

    @staticmethod
    def __build_language_inline_result(sorted_languages: List[Language], lang_code: str, url_prefix: str,
                                       markup: types.InlineKeyboardMarkup) -> types.InlineQueryResultVoice:
        """
        Finds the index of a x code in collection sorted_languages and returns an inline
        result for that specific x.

        :param sorted_languages: List of sorted Languages.
        :param lang_code: Language for the inline result.
        :param url_prefix: Url prefix.
        :param markup: Inline keyboard markup.
        :return: Inline result.
        :rtype: types.InlineQueryResultVoice
        """
        lang_index = Language.get_language_index_in_list(sorted_languages, lang_code)
        return types.InlineQueryResultVoice(
            str(lang_index + 1),
            url_prefix + sorted_languages[lang_index].code,
            sorted_languages[lang_index].title,
            reply_markup=markup
        )

    @staticmethod
    def update_chosen_results_tts_audio(chosen_result: types.ChosenInlineResult) -> None:
        """
        Update the number of times a x has been used based on a chosen inline result.

        :param chosen_result: Telegram chosen inline result.
        """
        db_conn = Utils.create_db_conn()
        sql_read = Constants.DBStatements.LAN_READ % str(chosen_result.from_user.id)
        result = db_conn.read_one(sql_read)
        if result:
            sorted_languages = Language.get_languages_sorted_for_user(result)
            lan = sorted_languages[int(chosen_result.result_id) - 1].code
            times = sorted_languages[int(chosen_result.result_id) - 1].record_use()
            sql_update = Constants.DBStatements.LAN_UPDATE_FOR_CHOSEN_RESULT % (lan, times, chosen_result.from_user.id)
            db_conn.write_all(sql_update)

    @staticmethod
    def store_tts_query(text: str, queries: OrderedDict) -> str:
        """
        Stores a text to speech query in a dictionary to use it later for callback query.

        :param text: Query from the user.
        :param queries: Query dictionary.
        :return: Code to identify query made by user.
        :rtype: Str.
        """
        code_id = Utils.generate_unique_str()
        if len(queries) >= Constants.MAX_QUERIES:
            queries.pop(next(reversed(queries)))
        queries[code_id] = text
        return code_id

    @staticmethod
    def get_callback_query_tts_audio(callback_code: str, queries: OrderedDict) -> Optional[str]:
        """
        Returns the text content of a text to speech audio based on the query done.

        :param callback_code: Callback code.
        :param queries: Dictionary that contains all created callbacks.
        :return: Text to speech audio description.
        :rtype: Str if exists audio with same callback code, None in other case.
        """
        try:
            return queries[callback_code]
        except KeyError:
            return None

    @staticmethod
    def generate_voice_content(query: str) -> str:
        """
        Generates and returns the prepared link to obtain all the possible audios.

        :param query:
        :return:
        """
        normalized_text = urllib.parse.quote(query)
        return Constants.TTS_STR.format(query=normalized_text)

    @staticmethod
    def is_arabic(text: str) -> bool:
        """
        Returns true is text contains Arabic x characters, false in other case.

        :param text: text to be checked.
        :return: True if is Arabic, false in other case.
        """
        return bool(re.search(TTSAudio.REGEX_ARABIC, text))

    @staticmethod
    def is_japanese(text: str) -> bool:
        """
        Returns true is text contains Japanese x characters, false in other case.

        :param text: text to be checked.
        :return: True if is Japanese, false in other case.
        """
        return bool(re.search(TTSAudio.REGEX_JAPANESE, text))

    @staticmethod
    def is_chinese(text: str) -> bool:
        """
        Returns true is text contains Chinese x characters, false in other case.

        :param text: text to be checked.
        :return: True if is Chinese, false in other case.
        """
        return bool(re.search(TTSAudio.REGEX_CHINESE, text))

    @staticmethod
    def is_korean(text: str) -> bool:
        """
        Returns true is text contains Korean x characters, false in other case.

        :param text: text to be checked.
        :return: True if is Korean, false in other case.
        """
        return bool(re.search(TTSAudio.REGEX_KOREAN, text))

    @staticmethod
    def is_cjk(text: str) -> bool:
        """
        Returns true is text contains Chinese, Japanese, Korean or other Chinese derivatives characters,
        false in other case.

        :param text: text to be checked.
        :return: True if is CJK, false in other case.
        """

        # regex = "/[\u3000-\u303F]|[\u3040-\u309F]|[\u30A0-\u30FF]|[\uFF00-\uFFEF]" + \
        #         "|[\u4E00-\u9FAF]|[\u2605-\u2606]|[\u2190-\u2195]|\u203B/g"
        return TTSAudio.is_korean(text) or TTSAudio.is_japanese(text) or TTSAudio.is_chinese(text)
