# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing LiteralConstants class.
"""

import enum
from collections import OrderedDict
from operator import itemgetter
from typing import Dict, List
from helpers.logger import Logger


class LiteralConstants:
    """
    Basic constants for the working of the project.

    All these constants are written in this python file shared across the project.
    """

    class FileType(enum.Enum):
        """ Enumerable with different file types that can be handled by the project. """
        REG = 1
        JSON = 2
        BYTES = 3

    class ChatType:
        """ Supported telegram chat types by the bot. """
        PRIVATE: str = "private"
        GROUP: str = "group"

    class BotCommands:
        """ Available commands for Txt2SpeechBot. """
        HELP: str = "help"
        START: str = "start"
        ADD_AUDIO: str = "addaudio"
        LST_AUDIO: str = "listaudio"
        RM_AUDIO: str = "rmaudio"
        RM_ALL_AUDIOS: str = "rmallaudios"

    class BotAnswers:
        """ Bot answers to user interaction. """
        SEND_AUDIO: str = "Send audio or voice note."
        MAX_OWN_AUDIOS: str = "Sorry, you reached maximun number of stored audios (50). Try removing some of them with /rmaudio command."
        PROVIDE_DESC: str = "Saved!\n\nProvide now a short description for the audio. 30 character allowed."
        NOT_AUDIO: str = "Audio file are not detected. Are you sure you've uploaded the correct file? Try it again with /addaudio command."
        WRONG_DESC: str = "Wrong input. Write a short description to save the audio. 30 characters maximum."
        USED_DESC: str = "Description is already in use. Please, write another one."
        SAVED: str = "Saved audio with description: \"%s\""
        LST_NONE_AUDIO: str = "Sorry, you don't have any uploaded audio... Try to upload one with /addaudio command."
        RM_AUDIO: str = "Send the description of the audio you want to remove."
        RM_ALL_AUDIO: str = "Are you completely sure you want to delete all your audios? Answer 'CONFIRM' in uppercase to verify this action."
        RM_ALL_NOT_CONFIRM: str = "You should have answered 'CONFIRM' to validate the deletion. Canceling action."
        RM_DESC_NOT_TEXT: str = "Wrong input. Send the description of the audio you want to remove. Try again /rmaudio."
        RM_USED_DESC: str = "No audio with the provided description. Please, send the correct description. Try again /rmaudio."
        DELETED_AUDIO: str = "The file was deleted from your audios."
        DELETED_ALL_AUDIO: str = "All your audios were deleted successfully."

    class FilePath:
        """ File path to required project files. """
        TOKEN: str = "data/token.txt"
        DB: str = "data/db.json"
        TTS: str = "data/magic.txt"
        HELP_MSG: str = "data/help.txt"
        STA_LOG: str = "data/status.log"
        MSG_LOG: str = "data/messages.log"
        QRY_LOG: str = "data/queries.log"

    class ExceptionMessages:
        """ Messages to be sent when a exception occurs. """
        DB_CONNECTED: str = "DB | Connected to MySQL database server, version "
        DB_UNCONNECTED: str = "DB | Error while trying to connect to MySQL database server\nError: "
        DB_DISCONNECTED: str = "DB | Disconnected from MySQL database server"
        DB_READ: str = "DB | Unable to fetch data from database\nSQL query: "
        DB_WRITE: str = "DB | Unable to write data in database\nSQL query: "
        FILE_CANT_OPEN: str = "File | Unable to open requested file\n"
        FILE_CANT_WRITE: str = "File | Unable to write provided data in this file\n"
        AUDIO_ERROR: str = "AUDIO | Unable to open file with mimetype %s\n"
        UNEXPECTED_ERROR: str = "Error | An unexpected error has occured\n"

    STA_LOG: Logger = Logger("Status log", FilePath.STA_LOG)
    MSG_LOG: Logger = Logger("Message logger", FilePath.MSG_LOG)
    QRY_LOG: Logger = Logger("Query logger", FilePath.QRY_LOG)

    MAX_QUERIES: int = 100000

    LANGUAGES: Dict[str, str] = {
        "AR العربية": "Ar",
        "Deutsch DE": "De-de",
        "English UK": "En-uk",
        "English US": "En-us",
        "Español ES": "Es-es",
        "Español MX": "Es-mx",
        "Français FR": "Fr-fr",
        "Italiano IT": "It-it",
        "Português PT": "Pt-pt",
        "ελληνικά GR": "El-gr",
        "русский RU": "Ru-ru",
        "Türkçe TR": "Tr-tr",
        "汉语 ZH": "Zh-cn",
        "日本語 JA": "Ja",
        "Polski PL": "Pl"
    }
    # noinspection PyTypeChecker
    SORTED_LANGUAGES: OrderedDict = OrderedDict(sorted(LANGUAGES.items(), key=itemgetter(0)))

    PROBLEMATIC_CHARS: Dict[str, str] = {
        "\n": " ",
        "’": "'",
        "‘": "'",
        "\"": "'",
        "“": "'",
        "”": "'",
        "…": "...",
        "<": "",
        ">": "",
        "#": "",
        "%": "",
        "{": "",
        "}": "",
        "|": "",
        "^": "",
        "~": "",
        "[": "",
        "]": "",
        "`": "",
        ";": "",
        "/": ""
    }  # ? : @ = &

    CONTENT_TYPES: List[str] = ['audio', 'voice', 'video']
    MIME_TYPES: List[str] = ['audio', 'video']
