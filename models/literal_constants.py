#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
from operator import itemgetter
from enum import Enum
from models.logger import Logger


class Literal_Constants:
    STATUS_LOG = Logger( "Status log", "data/status.log" )
    MSG_LOG = Logger( "Message logger", "data/messages.log" )
    QRY_LOG = Logger( "Query logger", "data/queries.log" )

    class FileType(Enum):
        REG = 1
        JSON = 2

    class ChatType:
        PRIVATE = "private"
        GROUP = "group"

    class FilePath:
        TOKEN = "data/token.txt"
        DB = "data/db.json"
        TTS = "data/magic.txt"
        HELP_MESSAGE = "data/help.txt"

    class ExceptionMessages:
        DB_CONNECTED = "DB | Connected to MySQL database server, version "
        DB_UNCONNECTED = "DB | Error while trying to connect to MySQL database server\nError: "
        DB_DISCONNECTED = "DB | Disconnected from MySQL database server"
        DB_READ = "DB | Unable to fetch data from database\nSQL query: "
        DB_WRITE = "DB | Unable to write data in database\nSQL query: "
        FILE_CANT_OPEN = "File | Unable to open requested file\n"
        FILE_CANT_WRITE = "File | Unable to write provided data in this file\n"
        UNEXPECTED_ERROR = "Error | An unexpected error has occured\n"

    MAX_QUERIES = 100000

    LANGUAGES = {
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
    SORTED_LANGUAGES = OrderedDict( sorted( LANGUAGES.items( ), key = itemgetter( 0 ) ) )

    PROBLEMATIC_CHARS = {
        "\n": " ",
        "’": "'",
        "\"": "'",
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
