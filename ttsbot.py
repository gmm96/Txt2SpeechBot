# !/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import telebot
import requests
import time
import magic
from telebot import types
from typing import List, Callable, Dict, Optional
from collections import OrderedDict
from pydub import AudioSegment
from io import BytesIO
from models.constants import Constants
from models.utils import Utils
from models.fileProcessing import FileProcessing


class Text_To_Speech_Bot(Utils):

    def __init__(self, bot: telebot.TeleBot):
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
        db_conn = self.create_db_conn()
        for message in messages:
            self.store_user(message.from_user, db_conn)
            self.record_message(message)

    def next_step(self, input_message: types.Message, text_to_send: str, function: Callable) -> None:
        reply = self.bot.reply_to(input_message, text_to_send, reply_markup=types.ForceReply(selective=False))
        self.bot.register_next_step_handler(reply, function)

    def convert_to_voice(self, desc_msg: types.Message, file_msg: types.Message) -> Optional[types.Message]:
        if file_msg.content_type == 'audio':
            file_link = file_msg.audio
        elif file_msg.content_type == 'video':
            file_link = file_msg.video
        else:
            file_link = file_msg.document

        downloaded_file = self.bot.download_file(self.bot.get_file(file_link.file_id).file_path)
        filename = Constants.FilePath.AUDIOS + str(file_link.file_id)
        self.bot.send_message(file_msg.from_user.id, "Parsing file to telegram voice format")
        try:
            song = AudioSegment.from_file(BytesIO(downloaded_file))
            song.export(filename, format="ogg", codec="libvorbis")
        except:
            mimetype = magic.from_file(filename, mime=True)
            Constants.STA_LOG.logger.exception(Constants.ExceptionMessages.AUDIO_ERROR % mimetype, exc_info=True)
            self.bot.send_message(6216877, 'Error trying to parse file with mimetype %s.' % mimetype)
            self.bot.reply_to(file_msg, "Unknown file format %s. Please, send another media file." % mimetype)
            return None
        else:
            voice = FileProcessing(filename, Constants.FileType.BYTES).read_file()
            new_msg = self.bot.send_voice(file_msg.from_user.id, voice)
            self.next_step_focused[str(desc_msg.from_user.id)] = file_msg = new_msg
            return file_msg
        finally:
            os.remove(filename)


my_bot = telebot.TeleBot(Constants.TOKEN)
tts = Text_To_Speech_Bot(my_bot)


@my_bot.message_handler(commands=[Constants.BotCommands.START, Constants.BotCommands.HELP])
def command_help(message: types.Message) -> None:
    tts.bot.send_message(message.from_user.id, Constants.HELP_MSG)


@my_bot.inline_handler(lambda query: 0 <= len(query.query) <= 201)
def query_handler(q: types.InlineQuery) -> None:
    db_conn = tts.create_db_conn()
    tts.store_user(q.from_user, db_conn)
    tts.record_query(q)
    if not q.query:
        inline_results = tts.create_inline_results_personal_audio(q, db_conn)
    else:
        inline_results = tts.create_inline_results_tts_audio(q, tts.queries, db_conn)
    try:
        tts.bot.answer_inline_query(q.id, inline_results, cache_time=1)
    except Exception as query_exc:
        Constants.STA_LOG.logger.exception('Query: "' + q.query + '"', exc_info=True)
        tts.bot.send_message(6216877, 'Query: "' + q.query + '"\n' + str(query_exc))


@my_bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def chosen_result_handler(chosen_inline_result: types.ChosenInlineResult) -> None:
    db_conn = tts.create_db_conn()
    if len(chosen_inline_result.query) == 0:
        tts.update_chosen_results_personal_audio(chosen_inline_result, db_conn)
    else:
        tts.update_chosen_results_tts_audio(chosen_inline_result, db_conn)


@my_bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(callback: types.CallbackQuery) -> None:
    db_conn = tts.create_db_conn()
    text = tts.get_callback_query(callback, tts.queries, db_conn)
    if len(text) > 54:
        tts.bot.answer_callback_query(callback.id, text, show_alert=True)
    else:
        tts.bot.answer_callback_query(callback.id, text)


@my_bot.message_handler(commands=[Constants.BotCommands.ADD_AUDIO])
def add_audio_start(m: types.Message) -> None:
    db_conn = tts.create_db_conn()
    result = db_conn.read_one(Constants.DBStatements.DB_AUDIOS_READ_COUNT % str(m.from_user.id))
    if result is not None and result[0] < 50:
        tts.next_step(m, Constants.BotAnswers.SEND_AUDIO, add_audio_file)
    else:
        tts.bot.reply_to(m, Constants.BotAnswers.MAX_OWN_AUDIOS)


def add_audio_file(m: types.Message) -> None:
    if tts.is_file_media(m):
        tts.next_step_focused[str(m.from_user.id)] = m
        tts.next_step(m, Constants.BotAnswers.PROVIDE_DESC, add_audio_description)
    else:
        tts.bot.reply_to(m, Constants.BotAnswers.NOT_AUDIO)


def add_audio_description(m: types.Message) -> None:
    db_conn = tts.create_db_conn()
    description = tts.db_str(m.text.strip())
    if m.content_type == 'text' and len(description) <= 30:
        result = db_conn.read_one(Constants.DBStatements.DB_AUDIO_READ_FOR_CHECKING % (str(m.from_user.id), description))
        if result is None:
            file_message = tts.next_step_focused[str(m.from_user.id)]
            if tts.should_convert_to_voice(file_message):
                file_message = tts.convert_to_voice(m, file_message)
                if not file_message:
                    return

            file_link = file_message.voice
            dbreturn = db_conn.read_all(Constants.DBStatements.DB_AUDIO_READ_USER_IDS % str(m.from_user.id))
            if len(dbreturn) > 0:
                taken_ids = [audio_id[0] for audio_id in dbreturn]
                user_audio_id = tts.get_free_user_audio_id(taken_ids)
            else:
                user_audio_id = 1
            callback_code = tts.generate_callback_code_for_own_audios()
            db_conn.write_all(Constants.DBStatements.DB_AUDIO_INSERT % (file_link.file_id, str(m.from_user.id),
                                                                        description, file_link.duration,
                                                                        file_link.file_size, user_audio_id,
                                                                        callback_code))
            tts.bot.reply_to(file_message, Constants.BotAnswers.SAVED % description)
        else:
            tts.next_step(m, Constants.BotAnswers.USED_DESC, add_audio_description)
    else:
        tts.next_step(m, Constants.BotAnswers.WRONG_DESC, add_audio_description)


@my_bot.message_handler(commands=[Constants.BotCommands.LST_AUDIO])
def list_own_audio(m: types.Message) -> None:
    db_conn = tts.create_db_conn()
    audio_str_list = tts.get_own_audios(m.from_user, db_conn)
    if audio_str_list is not None:
        tts.bot.reply_to(m, audio_str_list)
    else:
        tts.bot.reply_to(m, Constants.BotAnswers.LST_NONE_AUDIO)


@my_bot.message_handler(commands=[Constants.BotCommands.RM_AUDIO])
def rm_audio_start(m: types.Message) -> None:
    list_own_audio(m)
    db_conn = tts.create_db_conn()
    result = db_conn.read_one(Constants.DBStatements.DB_AUDIOS_READ_FOR_REMOVING % str(m.from_user.id))
    if result is not None:
        tts.next_step(m, Constants.BotAnswers.RM_AUDIO, rm_audio_select)


def rm_audio_select(m: types.Message) -> None:
    if m.content_type == 'text':
        db_conn = tts.create_db_conn()
        result = db_conn.read_one(Constants.DBStatements.DB_AUDIO_READ_FOR_CHECKING % (str(m.from_user.id),
                                                                                       tts.db_str(m.text.strip())))
        if result is not None:
            db_conn.write_all(Constants.DBStatements.DB_AUDIO_REMOVE % (str(m.from_user.id),
                                                                        tts.db_str(m.text.strip())))
            tts.bot.reply_to(m, Constants.BotAnswers.DELETED_AUDIO)
        else:
            tts.bot.reply_to(m, Constants.BotAnswers.RM_USED_DESC)
    else:
        tts.bot.reply_to(m, Constants.BotAnswers.RM_DESC_NOT_TEXT)


@my_bot.message_handler(commands=[Constants.BotCommands.RM_ALL_AUDIOS])
def rm_all_audios(m: types.Message) -> None:
    list_own_audio(m)
    db_conn = tts.create_db_conn()
    result = db_conn.read_one(Constants.DBStatements.DB_AUDIOS_READ_FOR_REMOVING % str(m.from_user.id))
    if result is not None:
        tts.next_step(m, Constants.BotAnswers.RM_ALL_AUDIO, confirm_rm_all_audios)


def confirm_rm_all_audios(m: types.Message) -> None:
    if m.text and m.text == 'CONFIRM':
        db_conn = tts.create_db_conn()
        db_conn.write_all(Constants.DBStatements.DB_ALL_AUDIO_REMOVE % str(m.from_user.id))
        tts.bot.reply_to(m, Constants.BotAnswers.DELETED_ALL_AUDIO)
    else:
        tts.bot.reply_to(m, Constants.BotAnswers.RM_ALL_NOT_CONFIRM)


while True:
    try:
        tts.bot.polling(none_stop=True)
    except requests.exceptions.ConnectionError as requests_exc:
        Constants.STA_LOG.logger.exception(Constants.ExceptionMessages.UNEXPECTED_ERROR, exc_info=True)
        time.sleep(10)
