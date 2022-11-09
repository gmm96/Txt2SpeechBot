# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing Language class.
"""

from operator import attrgetter
from typing import List, Tuple
from helpers.constants import Constants


class Language:
    """
    Python class to represent a language in a Text to Speech Telegram Bot.

    A language instance contains a set of language title, language code and the number of times the
    language has been used by a certain user.
    """

    def __init__(self, title: str = '', code: str = '', times_used: int = 0) -> None:
        """
        Creates a language object ready to be used.

        :param title: Title of the language.
        :param code: Language code identifier.
        :param times_used: Number of times the language has been used.
        """
        self.title = title
        self.code = code
        self.times_used = times_used

    @classmethod
    def get_languages_sorted_alphabetically(cls) -> 'List[Language]':
        """
        Creates a list of languages sorted alphabetically based on title parameter.

        :return: List of languages sorted alphabetically.
        :rtype: List[Language].
        """
        return sorted(
            [cls(title, code) for title, code in Constants.SORTED_LANGUAGES.items()],
            key=attrgetter("title"),
        )

    @classmethod
    def get_languages_sorted_for_user(cls, db_result: Tuple[int]) -> 'List[Language]':
        """
        Creates a list of languages sorted for user input.

        This methods generates a list of languages sorted based in times_used parameter, being the
        firsts those which has been used more times.

        :param db_result: Result from database.
        :return: List of languages sorted for user.
        :rtype: List[Language].
        """
        return sorted(
            [cls(title, code, db_result[i]) for i, (title, code) in enumerate(Constants.SORTED_LANGUAGES.items())],
            key=attrgetter("times_used"),
            reverse=True
        )

    def record_use(self) -> int:
        """
        Updates times used to add one and returns the updated value.

        :return: Updated times_used parameter.
        :rtype: int.
        """

        self.times_used += 1
        return self.times_used

    def __str__(self) -> str:
        """
        String value of the language object.

        :return: String value.
        :rtype: Str.
        """
        return "Language %s \t|\t Code %s \t|\t Times used %i\n" % (self.title, self.code, self.times_used)

    def __repr__(self) -> str:
        """
        Small string value to represent a language object.

        :return: String representation.
        :rtype: Str.
        """
        return "Lang %s \t|\t Code %s \t|\t Used %i\n" % (self.title, self.code, self.times_used)

    @staticmethod
    def get_language_index_in_list(languages: 'List[Language]', lang_code: str) -> int:
        """
        Get the index of a Language in a list of them based on language code.

        :param languages: List of languages.
        :param lang_code: Language code identifier.
        :return: Position in list if exists, -1 if it doesn't exist.
        """
        try:
            return [language.code for language in languages].index(lang_code)
        except ValueError:
            return -1
