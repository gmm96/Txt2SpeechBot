# !/usr/bin/python3
# -*- coding: utf-8 -*-

import enum
from collections import OrderedDict
from operator import itemgetter
from typing import Dict, List, Tuple
from models.logger import Logger


class LiteralConstants:
    class FileType(enum.Enum):
        REG = 1
        JSON = 2
        BYTES = 3

    class ChatType:
        PRIVATE: str = "private"
        GROUP: str = "group"

    class BotCommands:
        HELP: str = "help"
        START: str = "start"
        ADD_AUDIO: str = "addaudio"
        LST_AUDIO: str = "listaudio"
        RM_AUDIO: str = "rmaudio"
        RM_ALL_AUDIOS: str = "rmallaudios"

    class BotAnswers:
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
        TOKEN: str = "data/token.txt"
        DB: str = "data/db.json"
        TTS: str = "data/magic.txt"
        HELP_MSG: str = "data/help.txt"
        STA_LOG: str = "data/status.log"
        MSG_LOG: str = "data/messages.log"
        QRY_LOG: str = "data/queries.log"
        AUDIOS: str = "audios/"

    class ExceptionMessages:
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
        "Türk TR": "Tr-tr",
        "中国 ZH": "Zh-cn",
        "日本の JA": "Ja",
        "Polski PL": "Pl"
    }
    __sortedLAN: List[Tuple[str, str]] = sorted(LANGUAGES.items(), key=itemgetter(0))
    SORTED_LANGUAGES: OrderedDict = OrderedDict(__sortedLAN)

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

    CONTENT_TYPE: List[str] = ['audio', 'voice', 'video']
