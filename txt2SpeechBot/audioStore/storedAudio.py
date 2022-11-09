# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing StoredAudio class.
"""

from telebot import types
from typing import List, Optional, Union, Tuple
from helpers.constants import Constants
from helpers.database import Database
from helpers.utils import Utils
from audioStore.audio import Audio


class StoredAudio:
    """
    Python class to manipulate a stored audio in a Telegram bot.

    This class could be considered as a set of utilities to deal with cached audios in Telegram
    system. Its main purpose it's to deal with inline queries, chosen inline queries and callback
    queries, but it also has auxiliary methods that complement its business logic, as some tools
    to check the mime type or which kind of file is attached to a Telegram message.
    """

    SIZE_LIMIT = 20 * 1024 * 1024
    """Limit in bytes for the file size."""

    @staticmethod
    def create_inline_results_stored_audio(query: types.InlineQuery) \
            -> List[Union[types.InlineQueryResultCachedVoice, types.InlineQueryResultArticle]]:
        """
        Creates and returns inline results for a user to answer an inline query about stored audios.

        :param query: Telegram inline query.
        :return: Inline results to answer a query.
        :rtype: List [types.InlineQueryResultCachedVoice or types.InlineQueryResultArticle]
        """
        db_conn = Utils.create_db_conn()
        sql_read = Constants.DBStatements.AUDIOS_READ_FOR_QUERY_BUILD % str(query.from_user.id)
        result = db_conn.read_all(sql_read)
        if len(result) > 0:
            return StoredAudio.__create_inline_results_with_audios(result)
        else:
            return StoredAudio.__create_inline_results_no_audios()

    @staticmethod
    def __create_inline_results_with_audios(db_result: List[Tuple]) -> List[types.InlineQueryResultCachedVoice]:
        """
        Returns inline results for an user with stored audios.

        :return: Inline results to answer a query.
        :rtype: List[types.InlineQueryResultCachedVoice]
        """
        inline_results = []
        audios = Audio.get_audio_list_for_inline_results(db_result)
        for audio in audios:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Description", callback_data=audio.callback_code))
            inline_results.append(types.InlineQueryResultCachedVoice(
                str(audio.user_audio_id), audio.file_id, audio.description, reply_markup=markup
            ))
        return inline_results

    @staticmethod
    def __create_inline_results_no_audios() -> List[types.InlineQueryResultArticle]:
        """
        Returns inline results for an user without stored audios.

        :return: Inline results to answer a query.
        :rtype: List[types.InlineQueryResultArticle]
        """
        msg_if_clicked = types.InputTextMessageContent(Constants.HELP_MSG)
        inline_results = [
            types.InlineQueryResultArticle(1, "No entries for personal audios", msg_if_clicked),
            types.InlineQueryResultArticle(2, "You can type to get a TextToSpeech audio", msg_if_clicked),
            types.InlineQueryResultArticle(3, "Or add a personal audio chatting me privately", msg_if_clicked)
        ]
        return inline_results

    @staticmethod
    def update_chosen_results_stored_audio(chosen_result: types.ChosenInlineResult) -> None:
        """
        Update the number of times a stored audio has been used based on a chosen inline result.

        :param chosen_result: Telegram chosen inline result.
        """
        db_conn = Utils.create_db_conn()
        sql_read = Constants.DBStatements.AUDIOS_READ_FOR_CHOSEN_RESULT % (str(chosen_result.from_user.id),
                                                                           int(chosen_result.result_id))
        result = db_conn.read_one(sql_read)
        if result:
            audio = Audio(file_id=result[0], times_used=result[1])
            sql_update = Constants.DBStatements.AUDIOS_UPDATE_FOR_CHOSEN_RESULT % (audio.record_use(), audio.file_id)
            db_conn.write_all(sql_update)

    @staticmethod
    def get_callback_query_stored_audio(callback_code: str) -> Optional[str]:
        """
        Returns the description of a stored audio based on the callback query code.

        :param callback_code: Callback code.
        :return: Stored audio description.
        :rtype: Str if exists audio with same callback code, None in other case.
        """
        db_conn = Utils.create_db_conn()
        audio = Audio(callback_code=callback_code)
        result = db_conn.read_one(Constants.DBStatements.AUDIOS_READ_FOR_CALLBACK_QUERY % callback_code)
        if result:
            audio.description = result[0]
            return audio.description
        else:
            return None

    @staticmethod
    def get_stored_audio_free_id(taken_ids: List[int]) -> Optional[int]:
        """
        Returns the first and lowest available stored audio identifier for a certain user.

        :param taken_ids: List of identifiers in use.
        :return: Stored user audio identifier.
        :rtype: Int if available user identifier, None in other case.
        """
        current_id, max_id = 1, 51
        while current_id in taken_ids and current_id < max_id:
            current_id += 1
        return current_id if current_id < max_id else None

    @staticmethod
    def get_stored_audios_listing(user_id: str, db_conn: Database) -> Optional[str]:
        """
        Returns a string containing a resume of all audios uploaded by a user.

        :param user_id: Telegram user identifier.
        :param db_conn: Database object
        :return: Str if exists audios, None in other case.
        """
        result = db_conn.read_all(Constants.DBStatements.AUDIOS_READ_FOR_LISTING % user_id)
        if len(result) == 0:
            return None
        audios = Audio.get_audio_list_for_listing(result)
        message = "These are your stored audios.\n\n"
        for index, audio in enumerate(audios):
            message += "%i.-  %s \t|\t %i s \t|\t %.2fKB\n" % (index + 1, audio.description,
                                                               audio.duration, audio.size / 1024.0)
        return message

    @staticmethod
    def is_file_valid_telegram_voice(content_type: str) -> bool:
        """
        Checks if file is a compatible Telegram voice audio.

        :param content_type: Type of content.
        :return: True if it is a voice, False in other case.
        :rtype: Bool.
        """
        return content_type == 'voice'

    @staticmethod
    def validate_multimedia_file(msg: types.Message) -> bool:
        """
        Checks and validates a multimedia file to be processed.

        :param msg: Telegram message.
        :return: True if it is valid, False in other case.
        :rtype: Bool
        """
        return StoredAudio.is_file_multimedia(msg) and \
               StoredAudio.has_multimedia_file_proper_size(msg)

    @staticmethod
    def is_file_multimedia(msg: types.Message) -> bool:
        """
        Scans Telegram message content type to check if has a multimedia attached file.

        :param msg: Telegram message.
        :return: True if it is multimedia, False in other case.
        :rtype: Bool
        """
        return msg.content_type in Constants.CONTENT_TYPES or StoredAudio.is_document_multimedia_file(msg)

    @staticmethod
    def has_multimedia_file_proper_size(msg: types.Message) -> bool:
        """
        Checks if the attached file to a Telegram message has lower size than limit.

        :param msg: Telegram message.
        :return: True if file size is lower than limit, False in other case.
        :rtype: Bool
        """
        return StoredAudio.get_file_link(msg).file_size <= StoredAudio.SIZE_LIMIT

    @staticmethod
    def is_document_multimedia_file(msg: types.Message) -> bool:
        """
        Checks if a Telegram document attached to a Telegram message is a multimedia file.

        :param msg: Telegram message.
        :return: True if it is multimedia, False in other case.
        :rtype: Bool.
        """
        if msg.content_type == 'document':
            file_type = StoredAudio.get_type_from_mime_type(msg.document.mime_type)
            if file_type in Constants.MIME_TYPES:
                return True

        return False

    @staticmethod
    def get_type_from_mime_type(mime_type: str) -> str:
        """
        Returns the type of file according to the mime_type.

        :param mime_type: File's mime type.
        :return: Type of file.
        :rtype: Str.
        """
        return mime_type.split('/')[0]

    @staticmethod
    def get_file_link(msg: types.Message) -> Union[types.Voice, types.Audio, types.Video, types.Document]:
        """
        Returns a file link from a Telegram message based on the content file type.

        :param msg: Telegram message.
        :return: Link to the contained file.
        :rtype: Voice, audio, video or document.
        """
        if msg.content_type == 'voice':
            return msg.voice
        elif msg.content_type == 'audio':
            return msg.audio
        elif msg.content_type == 'video':
            return msg.video
        elif msg.content_type == 'document':
            return msg.document
