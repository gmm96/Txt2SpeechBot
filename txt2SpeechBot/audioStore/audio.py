# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing Audio class.
"""

from operator import attrgetter
from typing import List, Tuple


class Audio:
    """
    Python class to represent a cached audio in Telegram system.

    These audios aren't written in disk, they're cached in Telegram system, so we can use them
    without the requirement of downloading the file in our filesystem.
    """

    def __init__(self, file_id: str = "", user_id: str = "", description: str = "", duration: int = 0,
                 size: int = 0, user_audio_id: int = 0, callback_code: str = 0, times_used: int = 0) -> None:
        """
        Creates a object that represent a cached audio in Telegram.

        :param file_id: File identifier.
        :param user_id: Telegram user identifier.
        :param description: Description of the audio.
        :param duration: Duration in seconds.
        :param size: Size in bytes.
        :param user_audio_id: Identifier of the audio in the user's list.
        :param callback_code: Callback code to obtain the description.
        :param times_used: Number of times the audio has been used.
        """
        self.file_id = file_id
        self.user_id = user_id
        self.description = description
        self.duration = duration
        self.size = size
        self.user_audio_id = user_audio_id
        self.callback_code = callback_code
        self.times_used = times_used

    @classmethod
    def get_audio_list_for_inline_results(cls, db_result: List[Tuple[str, str, int, str, int]]) -> 'List[Audio]':
        """
        Returns a list of stored audios for a user so he can use them.

        :param db_result: Result from database to create inline results.
        :return: List with stored audios.
        :rtype: List[Audio].
        """
        return sorted([cls(
            file_id=audio_tuple[0],
            description=audio_tuple[1],
            user_audio_id=audio_tuple[2],
            callback_code=audio_tuple[3],
            times_used=audio_tuple[4]
            ) for audio_tuple in db_result],
            key=attrgetter("times_used")
        )

    @classmethod
    def get_audio_list_for_listing(cls,  db_result: List[Tuple]) -> 'List[Audio]':
        """
        Returns a list of stored audios for a user so he can view and check them.

        :param db_result: Result from database to create audio listing.
        :return: List with stored audios.
        :rtype: List[Audio].
        """
        return [cls(
            file_id=audio_tuple[0],
            description=audio_tuple[1],
            duration=audio_tuple[2],
            size=audio_tuple[3]
            ) for audio_tuple in db_result
        ]

    def record_use(self) -> int:
        """
        Updates times used to add one and returns the updated value.

        :return: Updated times_used parameter.
        :rtype: int.
        """
        self.times_used += 1
        return self.times_used
