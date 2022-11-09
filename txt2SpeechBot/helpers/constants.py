# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing Constants class.
"""

from typing import List
from helpers.literalConstants import LiteralConstants
from helpers.fileProcessing import FileProcessing


class Constants(LiteralConstants):
    """
    Constant values shared to all project.

    Class that contains the MySQL statements of this project and some constant values that needs to be
    read from the disk. It inheritances from the LiteralConstants class, so all its values can be accessed.
    """

    TOKEN: str = FileProcessing(LiteralConstants.FilePath.TOKEN, LiteralConstants.FileType.REG).read_file().rstrip()
    DB_CREDENTIALS: List[str] = FileProcessing(LiteralConstants.FilePath.DB, LiteralConstants.FileType.JSON).read_file()
    TTS_STR: str = FileProcessing(LiteralConstants.FilePath.TTS, LiteralConstants.FileType.REG).read_file()
    HELP_MSG: str = FileProcessing(LiteralConstants.FilePath.HELP_MSG, LiteralConstants.FileType.REG).read_file()

    class DBStatements:
        """ MySQL statements to perform operations in Database system. """

        USER_READ: str = """SELECT * FROM User_Info WHERE id = '%s'"""
        USER_INSERT: str = """INSERT INTO User_Info(id, username, first_name, last_name) VALUES ('%s', '%s', '%s', '%s')"""
        USER_UPDATE: str = """UPDATE User_Info SET username = '%s', first_name = '%s', last_name = '%s' WHERE id = '%s'"""
        """ Table User_Info """

        AUDIOS_READ_FOR_QUERY_BUILD: str = """SELECT `file_id`, `description`, `user_audio_id`, `callback_code`, `times_used` FROM Own_Audios WHERE id = '%s'"""
        AUDIOS_READ_FOR_CHOSEN_RESULT: str = """SELECT `file_id`, `times_used` FROM Own_Audios WHERE id = '%s' AND user_audio_id = '%i'"""
        AUDIOS_READ_FOR_CALLBACK_QUERY: str = """SELECT `description` FROM Own_Audios WHERE callback_code = '%s'"""
        AUDIOS_READ_COUNT: str = """SELECT COUNT(`file_id`) FROM Own_Audios WHERE id = '%s'"""
        AUDIOS_READ_FOR_CHECKING: str = """SELECT `file_id` FROM Own_Audios WHERE id = '%s' AND description = '%s'"""
        AUDIOS_READ_FOR_LISTING: str = """SELECT `file_id`, `description`, `duration`, `size` FROM Own_Audios WHERE id = '%s'"""
        AUDIOS_READ_FOR_REMOVING: str = """SELECT `file_id`, `description` FROM Own_Audios WHERE id = '%s'"""
        AUDIOS_READ_USER_IDS: str = """SELECT `user_audio_id` FROM Own_Audios WHERE id = '%s'"""
        AUDIOS_INSERT: str = """INSERT INTO Own_Audios(file_id, id, description, duration, size, user_audio_id, callback_code) VALUES ('%s', '%s', '%s', '%i', '%i', '%i', '%s')"""
        AUDIOS_UPDATE_FOR_CHOSEN_RESULT: str = """UPDATE Own_Audios SET `times_used` = '%i' WHERE file_id = '%s'"""
        AUDIOS_REMOVE: str = """DELETE FROM Own_Audios WHERE id = '%s' AND description = '%s'"""
        AUDIOS_REMOVE_ALL: str = """DELETE FROM Own_Audios WHERE id = '%s'"""
        """ Table Own_Audios """

        LAN_READ: str = """SELECT `""" + """`, `""".join(LiteralConstants.SORTED_LANGUAGES.values()) \
                        + """` FROM Lan_Results WHERE id = '%s'"""
        LAN_INSERT: str = """INSERT INTO Lan_Results(id) VALUES('%s')"""
        LAN_UPDATE_FOR_CHOSEN_RESULT: str = """UPDATE Lan_Results SET `%s` = '%d' WHERE id = '%s'"""
        """ Table Lan_Results """
