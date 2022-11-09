# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing Text_To_Speech_Bot class.
"""

import requests
import time
import telebot
import magic
from telebot import types
from typing import List, Callable, Dict, Optional
from collections import OrderedDict
from pydub import AudioSegment
from io import BytesIO
from helpers.constants import Constants
from helpers.database import Database
from helpers.utils import Utils
from helpers.user import User
from textToSpeech.ttsAudio import TTSAudio
from audioStore.storedAudio import StoredAudio


# region Bot Class

class Text_To_Speech_Bot(TTSAudio, StoredAudio):
    """
    Python helper class to manipulate a text to speech bot using Telegram API.
    """

    def __init__(self, bot: telebot.TeleBot):
        """
        Creates and properly initializes a Telegram inline bot ready to be used.

        :param bot: Telegram bot from API.
        """
        self.bot: telebot.TeleBot = bot
        self.bot.set_update_listener(self.listener)
        self.bot.enable_save_next_step_handlers(delay=3)
        self.bot.load_next_step_handlers()
        self.queries: OrderedDict = OrderedDict()
        self.next_step_focused: Dict[str, types.Message] = {}
        Constants.MSG_LOG.log_also_to_stdout()
        Constants.QRY_LOG.log_also_to_stdout()
        Constants.STA_LOG.log_also_to_stdout()

    def listener(self, messages: List) -> None:
        """
        Listens and deals with all Telegram messages processed by bot.

        :param messages: List of Telegram messages.
        """
        for msg in messages:
            User.validate_user_from_telegram(msg.from_user)
            Utils.record_message(msg)

    def get_callback_query(self, callback: types.CallbackQuery) -> str:
        """
        Returns the description of an audio sent by bot.

        :param callback: Callback query to answer.
        :return: Audio description.
        :rtype: Str.
        """
        if text := self.get_callback_query_stored_audio(callback.data):
            return text
        elif text := self.get_callback_query_tts_audio(callback.data, self.queries):
            return text
        else:
            return ""

    def next_step(self, input_msg: types.Message, text_to_send: str, function: Callable) -> None:
        """
        Register the next action the bot should take. This method is helpful for multiple steps
        processes.

        :param input_msg: Telegram user message to reply.
        :param text_to_send: Text to be sent in bot reply.
        :param function: Next step to be processed.
        """
        reply = self.bot.reply_to(input_msg, text_to_send, reply_markup=types.ForceReply(selective=False))
        self.bot.register_next_step_handler(reply, function)

    def convert_to_voice(self, desc_msg: types.Message, file_msg: types.Message) -> Optional[types.Message]:
        """
        Converts any supported multimedia file in a Telegram compatible voice format.

        :param desc_msg: Telegram message containing audio description.
        :param file_msg: Telegram message containing audio file.
        """
        file_link = self.get_file_link(file_msg)
        downloaded_file = self.bot.download_file(self.bot.get_file(file_link.file_id).file_path)
        self.bot.send_message(file_msg.from_user.id, "Parsing file to telegram voice format")
        try:
            song = AudioSegment.from_file(BytesIO(downloaded_file))
            io_file = BytesIO()
            song.export(io_file, format="ogg", codec="libvorbis")
        except:
            mimetype = magic.from_buffer(downloaded_file, mime=True)
            Constants.STA_LOG.logger.exception(Constants.ExceptionMessages.AUDIO_ERROR % mimetype, exc_info=True)
            self.bot.send_message(6216877, 'Error trying to parse file with mimetype %s.' % mimetype)
            self.bot.reply_to(file_msg, "Unknown file format %s. Please, send another media file." % mimetype)
            return None
        else:
            new_msg = self.bot.send_voice(file_msg.from_user.id, io_file.read())
            self.next_step_focused[str(desc_msg.from_user.id)] = new_msg
            return new_msg

# endregion


my_bot = telebot.TeleBot(Constants.TOKEN)
tts = Text_To_Speech_Bot(my_bot)


# region Inline Mode

@my_bot.inline_handler(lambda query: 0 <= len(query.query) <= 201)
def query_handler(query: types.InlineQuery) -> None:
    """
    Answers with different purpose audios an inline query from an user.

    :param query: Telegram query.
    """
    User.validate_user_from_telegram(query.from_user)
    Utils.record_query(query)
    if not query.query:
        inline_results = tts.create_inline_results_stored_audio(query)
    else:
        inline_results = tts.create_inline_results_tts_audio(query, tts.queries)
    try:
        tts.bot.answer_inline_query(str(query.id), inline_results, cache_time=1)
    except Exception as query_exc:
        Constants.STA_LOG.logger.exception('Query: "' + query.query + '"', exc_info=True)
        tts.bot.send_message(6216877, 'Query: "' + query.query + '"\n' + str(query_exc))


@my_bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def chosen_result_handler(chosen_inline_result: types.ChosenInlineResult) -> None:
    """
    Updates previous database record with the selected inline result.

    :param chosen_inline_result: Telegram chosen inline result.
    """
    if len(chosen_inline_result.query) == 0:
        tts.update_chosen_results_stored_audio(chosen_inline_result)
    else:
        tts.update_chosen_results_tts_audio(chosen_inline_result)
    # tts.bot.send_message(6216877, 'a' + str(chosen_inline_result))


@my_bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(callback: types.CallbackQuery) -> None:
    """
    Provides the user a description of the sent audio.

    :param callback: Telegram callback query.
    """
    text = tts.get_callback_query(callback)
    if len(text) > 54:
        tts.bot.answer_callback_query(callback.id, text, show_alert=True)
    else:
        tts.bot.answer_callback_query(callback.id, text)

# endregion


# region Bot Commands

@my_bot.message_handler(commands=[Constants.BotCommands.START, Constants.BotCommands.HELP])
def command_help(msg: types.Message) -> None:       # TODO improve help message
    """
    Answers the user with a help message to help him to understand the purpose of this bot.

    :param msg: Telegram message with /help command.
    """
    tts.bot.send_message(msg.from_user.id, Constants.HELP_MSG)


@my_bot.message_handler(commands=[Constants.BotCommands.ADD_AUDIO])
def add_audio_start(msg: types.Message) -> None:
    """
    Initializes the process of audio uploading for user (1/3 Add Audio).

    :param msg: Telegram message with /addaudio command.
    """
    db_conn = Utils.create_db_conn()
    result = db_conn.read_one(Constants.DBStatements.AUDIOS_READ_COUNT % str(msg.from_user.id))
    if result and result[0] < 50:
        tts.next_step(msg, Constants.BotAnswers.SEND_AUDIO, add_audio_file)
    else:
        tts.bot.reply_to(msg, Constants.BotAnswers.MAX_OWN_AUDIOS)


def add_audio_file(msg: types.Message) -> None:
    """
    Validates file received from user (2/3 Add Audio).

    :param msg: Telegram message with attached file.
    """
    if tts.validate_multimedia_file(msg):
        tts.next_step_focused[str(msg.from_user.id)] = msg
        tts.next_step(msg, Constants.BotAnswers.PROVIDE_DESC, add_audio_description)
    else:
        tts.bot.reply_to(msg, Constants.BotAnswers.NOT_AUDIO)


def add_audio_description(msg: types.Message) -> None:
    """
    Downloads audio file and saves it with its respective description (3/3 Add Audio).

    :param msg: Telegram message with audio description.
    """
    db_conn = Utils.create_db_conn()
    description = Database.db_str(msg.text.strip())
    if msg.content_type == 'text' and len(description) <= 30:
        user_id = str(msg.from_user.id)
        result = db_conn.read_one(Constants.DBStatements.AUDIOS_READ_FOR_CHECKING % (user_id, description))
        if result is None:
            file_message = tts.next_step_focused[str(msg.from_user.id)]
            if not tts.is_file_valid_telegram_voice(file_message.content_type):
                file_message = tts.convert_to_voice(msg, file_message)
                if not file_message:
                    return

            file_link = file_message.voice
            db_return = db_conn.read_all(Constants.DBStatements.AUDIOS_READ_USER_IDS % user_id)
            if len(db_return) > 0:
                taken_ids = [audio_id[0] for audio_id in db_return]
                user_audio_id = tts.get_stored_audio_free_id(taken_ids)
            else:
                user_audio_id = 1
            callback_code = Utils.generate_unique_str()
            db_conn.write_all(Constants.DBStatements.AUDIOS_INSERT % (file_link.file_id, user_id,
                                                                      description, file_link.duration,
                                                                      file_link.file_size, user_audio_id,
                                                                      callback_code))
            tts.bot.reply_to(file_message, Constants.BotAnswers.SAVED % description)
        else:
            tts.next_step(msg, Constants.BotAnswers.USED_DESC, add_audio_description)
    else:
        tts.next_step(msg, Constants.BotAnswers.WRONG_DESC, add_audio_description)


@my_bot.message_handler(commands=[Constants.BotCommands.LST_AUDIO])
def list_stored_audios(msg: types.Message) -> None:
    """
    Lists all the stored audios by a certain user and their details.

    :param msg: Telegram message with /listaudios command.
    """
    db_conn = Utils.create_db_conn()
    audio_str_list = tts.get_stored_audios_listing(str(msg.from_user.id), db_conn)
    if audio_str_list:
        tts.bot.reply_to(msg, audio_str_list)
    else:
        tts.bot.reply_to(msg, Constants.BotAnswers.LST_NONE_AUDIO)


@my_bot.message_handler(commands=[Constants.BotCommands.RM_AUDIO])
def rm_audio_start(msg: types.Message) -> None:
    """
    Lists all the stored audios by a certain user asks him to delete one of them
    (1/2 Remove One Audio).

    :param msg: Telegram message with /rmaudio command.
    """
    list_stored_audios(msg)
    db_conn = Utils.create_db_conn()
    result = db_conn.read_one(Constants.DBStatements.AUDIOS_READ_FOR_REMOVING % str(msg.from_user.id))
    if result:
        tts.next_step(msg, Constants.BotAnswers.RM_AUDIO, rm_audio_select)


def rm_audio_select(msg: types.Message) -> None:
    """
    Removes an uploaded audio by a determined user if description equals the received
    message from that user (2/2 Remove One Audio).

    :param msg: Telegram message with removing confirmation.
    """
    if msg.content_type == 'text' and msg.text:
        db_conn = Utils.create_db_conn()
        audio_to_rm = Database.db_str(msg.text.strip())
        user_id = str(msg.from_user.id)
        result = db_conn.read_one(Constants.DBStatements.AUDIOS_READ_FOR_CHECKING % (user_id, audio_to_rm))
        if result:
            db_conn.write_all(Constants.DBStatements.AUDIOS_REMOVE % (user_id, audio_to_rm))
            tts.bot.reply_to(msg, Constants.BotAnswers.DELETED_AUDIO)
        else:
            tts.bot.reply_to(msg, Constants.BotAnswers.RM_USED_DESC)
    else:
        tts.bot.reply_to(msg, Constants.BotAnswers.RM_DESC_NOT_TEXT)


@my_bot.message_handler(commands=[Constants.BotCommands.RM_ALL_AUDIOS])
def rm_all_audios(msg: types.Message) -> None:
    """
    Lists all the stored audios by a certain user asks him to delete all of them.
    (2/2 Remove All Audios)

    :param msg: Telegram message with /rmallaudios command.
    """
    list_stored_audios(msg)
    db_conn = Utils.create_db_conn()
    result = db_conn.read_one(Constants.DBStatements.AUDIOS_READ_FOR_REMOVING % str(msg.from_user.id))
    if result:
        tts.next_step(msg, Constants.BotAnswers.RM_ALL_AUDIO, confirm_rm_all_audios)


def confirm_rm_all_audios(msg: types.Message) -> None:
    """
    Removes all previous uploaded audios by a determined user (2/2 Remove All Audios).

    :param msg: Telegram message with removing confirmation.
    """
    if msg.content_type == 'text' and msg.text and msg.text.strip() == 'CONFIRM':
        db_conn = Utils.create_db_conn()
        remove_result = db_conn.write_all(Constants.DBStatements.AUDIOS_REMOVE_ALL % str(msg.from_user.id))
        if remove_result:
            tts.bot.reply_to(msg, Constants.BotAnswers.DELETED_ALL_AUDIO)
    else:
        tts.bot.reply_to(msg, Constants.BotAnswers.RM_ALL_NOT_CONFIRM)

# endregion


while True:
    try:
        tts.bot.polling(none_stop=True)
    except requests.exceptions.ConnectionError as requests_exc:
        Constants.STA_LOG.logger.exception(Constants.ExceptionMessages.UNEXPECTED_ERROR, exc_info=True)
        time.sleep(10)
