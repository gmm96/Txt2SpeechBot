# !/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import List
from models.literalConstants import LiteralConstants
from models.fileProcessing import FileProcessing


class Constants(LiteralConstants):
    TOKEN: str = FileProcessing(LiteralConstants.FilePath.TOKEN, LiteralConstants.FileType.REG).read_file().rstrip()
    DB_CREDENTIALS: List[str] = FileProcessing(LiteralConstants.FilePath.DB, LiteralConstants.FileType.JSON).read_file()
    TTS_STR: str = FileProcessing(LiteralConstants.FilePath.TTS, LiteralConstants.FileType.REG).read_file()
    HELP_MSG: str = FileProcessing(LiteralConstants.FilePath.HELP_MSG, LiteralConstants.FileType.REG).read_file()

    class DBStatements:
        """ Table User_Info """
        DB_USER_READ: str = """SELECT * FROM User_Info WHERE id = '%s'"""
        DB_USER_INSERT: str = """INSERT INTO User_Info(id, username, first_name, last_name) VALUES ('%s', '%s', '%s', '%s')"""
        DB_USER_UPDATE: str = """UPDATE User_Info SET username = '%s', first_name = '%s', last_name = '%s' WHERE id = '%s'"""
        """ Table Own_Audios """
        DB_AUDIOS_READ_FOR_QUERY_BUILD: str = """SELECT `file_id`, `description`, `user_audio_id`, `callback_code` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIOS_READ_FOR_CHOSEN_RESULT: str = """SELECT `file_id`, `times_used` FROM Own_Audios WHERE id = '%s' AND user_audio_id = '%i'"""
        DB_AUDIOS_READ_FOR_CALLBACK_QUERY: str = """SELECT `description` FROM Own_Audios WHERE callback_code = '%s'"""
        DB_AUDIOS_READ_COUNT: str = """SELECT COUNT(`file_id`) FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIO_READ_FOR_CHECKING: str = """SELECT `file_id` FROM Own_Audios WHERE id = '%s' AND description = '%s'"""
        DB_AUDIOS_READ_FOR_LISTING: str = """SELECT `file_id`, `description`, `duration`, `size` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIOS_READ_FOR_REMOVING: str = """SELECT `file_id`, `description` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIO_READ_USER_IDS: str = """SELECT `user_audio_id` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIO_INSERT: str = """INSERT INTO Own_Audios(file_id, id, description, duration, size, user_audio_id, callback_code) VALUES ('%s', '%s', '%s', '%i', '%i', '%i', '%s')"""
        DB_AUDIO_UPDATE_FOR_CHOSEN_RESULT: str = """UPDATE Own_Audios SET `times_used` = '%i' WHERE file_id = '%s'"""
        DB_AUDIO_REMOVE: str = """DELETE FROM Own_Audios WHERE id = '%s' AND description = '%s'"""
        DB_ALL_AUDIO_REMOVE: str = """DELETE FROM Own_Audios WHERE id = '%s'"""
        """ Table Lan_Results """
        DB_LAN_READ: str = """SELECT `""" + """`, `""".join(LiteralConstants.SORTED_LANGUAGES.values()) \
                           + """` FROM Lan_Results WHERE id = '%s'"""
        DB_LAN_INSERT: str = """INSERT INTO Lan_Results(id) VALUES('%s')"""
        DB_LAN_UPDATE_FOR_CHOSEN_RESULT: str = """UPDATE Lan_Results SET `%s` = '%d' WHERE id = '%s'"""
