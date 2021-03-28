#!/usr/bin/python3
# -*- coding: utf-8 -*-

from models.literal_constants import Literal_Constants
from models.file_processing import File_Processing

class Constants( Literal_Constants ):
    TOKEN = File_Processing( Literal_Constants.FilePath.TOKEN, Literal_Constants.FileType.REG ).read_file( ).rstrip()
    DB_CREDENTIALS = File_Processing( Literal_Constants.FilePath.DB, Literal_Constants.FileType.JSON ).read_file( )
    TTS_STR = File_Processing( Literal_Constants.FilePath.TTS, Literal_Constants.FileType.REG ).read_file( )
    HELP_MESSAGE = File_Processing( Literal_Constants.FilePath.HELP_MESSAGE, Literal_Constants.FileType.REG ).read_file( )

    class DBStatements:
        """ Table User_Info """
        DB_USER_READ = """SELECT * FROM User_Info WHERE id = '%s'"""
        DB_USER_INSERT = """INSERT INTO User_Info(id, username, first_name, last_name) VALUES ('%s', '%s', '%s', '%s')"""
        DB_USER_UPDATE = """UPDATE User_Info SET username = '%s', first_name = '%s', last_name = '%s' WHERE id = '%s'"""
        """ Table Own_Audios """
        DB_AUDIOS_READ_FOR_QUERY_BUILD = """SELECT `file_id`, `description`, `user_audio_id`, `callback_code` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIOS_READ_FOR_CHOSEN_RESULT = """SELECT `file_id`, `times_used` FROM Own_Audios WHERE id = '%s' AND user_audio_id = '%i'"""
        DB_AUDIOS_READ_FOR_CALLBACK_QUERY = """SELECT `description` FROM Own_Audios WHERE callback_code = '%s'"""
        DB_AUDIOS_READ_COUNT = """SELECT COUNT(`file_id`) FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIO_READ_FOR_CHECKING = """SELECT `file_id` FROM Own_Audios WHERE id = '%s' AND description = '%s'"""
        DB_AUDIOS_READ_FOR_LISTING = """SELECT `file_id`, `description`, `duration`, `size` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIOS_READ_FOR_REMOVING = """SELECT `file_id`, `description` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIO_READ_USER_IDS = """SELECT `user_audio_id` FROM Own_Audios WHERE id = '%s'"""
        DB_AUDIO_INSERT = """INSERT INTO Own_Audios(file_id, id, description, duration, size, user_audio_id, callback_code) VALUES ('%s', '%s', '%s', '%i', '%i', '%i', '%s')"""
        DB_AUDIO_UPDATE_FOR_CHOSEN_RESULT = """UPDATE Own_Audios SET `times_used` = '%i' WHERE file_id = '%s'"""
        DB_AUDIO_REMOVE = """DELETE FROM Own_Audios WHERE id = '%s' AND description = '%s'"""
        """ Table Lan_Results """
        DB_LAN_READ = """SELECT `""" + """`, `""".join(Literal_Constants.SORTED_LANGUAGES.values()) + """` FROM Lan_Results WHERE id = '%s'"""
        DB_LAN_INSERT = """INSERT INTO Lan_Results(id) VALUES('%s')"""
        DB_LAN_UPDATE_FOR_CHOSEN_RESULT = """UPDATE Lan_Results SET `%s` = '%d' WHERE id = '%s'"""
