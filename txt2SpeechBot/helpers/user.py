# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing User class.
"""

from telebot import types
from typing import Optional
from helpers.constants import Constants
from helpers.database import Database
from helpers.utils import Utils


class User:
    """
    Python class to represent an user in our bot application system.

    This class could be considered as an additional layer between Telegram user and users stored
    in database. Created to simplify the way we deal with users in our application.
    """

    def __init__(self, internal_id: str = "", user_id: str = "", username: str = "", first_name: str = "",
                 last_name: str = "") -> None:
        """
        Creates a object that represent an user of the application.

        :param internal_id: Internal bot user identifier.
        :param user_id: Telegram user identifier.
        :param username: Telegram username.
        :param first_name: Telegram user's first name.
        :param last_name: Telegram user's second name.
        """
        self.internal_id = internal_id
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def __eq__(self, other_user: 'User') -> bool:
        """
        Checks if two instances of this class have equal values, so it could be considered the same
        user.

        :param other_user: User to check equality.
        :return: True if users have same values, False in other case.
        :rtype: Bool.
        """
        if type(self) is not type(other_user):
            return False

        return self.user_id == other_user.user_id and \
               self.username == other_user.username and \
               self.first_name == other_user.first_name and \
               self.last_name == other_user.last_name

    @classmethod
    def get_user_from_db(cls, user_id: str) -> Optional['User']:
        """
        Returns an user instance from database based on Telegram user identifier. If the user does
        not exist or did not use previously the bot application, returns None.

        :param user_id: Telegram user identifier.
        :return: User if exists records in database with Telegram user identifier.
        :rtype: User if exists, None in other case.
        """
        db_conn = Utils.create_db_conn()
        sql_read = Constants.DBStatements.USER_READ % str(user_id)
        result = db_conn.read_one(sql_read)
        return cls(
            internal_id=result[0],
            user_id=result[1],
            username=result[2],
            first_name=result[3],
            last_name=result[4]
        ) if result else None

    @classmethod
    def get_user_from_telegram_user(cls, user: types.User) -> 'User':
        """
        Returns a user instance based on Telegram user attached to a message or query.

        :param user: Telegram user from message or query.
        :return: User instance based on Telegram system.
        :rtype: User.
        """
        return cls(
            user_id=str(user.id),
            username=Database.db_str(user.username),
            first_name=Database.db_str(user.first_name),
            last_name=Database.db_str(user.last_name)
        )

    def store(self) -> None:
        """
        Initializes and stores an user in our bot application.
        """
        db_conn = Utils.create_db_conn()
        sql_insert_user_info = Constants.DBStatements.USER_INSERT % (self.user_id, self.username,
                                                                     self.first_name, self.last_name)
        sql_insert_chosen_result = Constants.DBStatements.LAN_INSERT % self.user_id
        db_conn.write_all(sql_insert_user_info)
        db_conn.write_all(sql_insert_chosen_result)

    def update(self) -> None:
        """
        Updates user's parameters in database.
        """
        sql_update = Constants.DBStatements.USER_UPDATE % (self.username, self.first_name, self.last_name, self.user_id)
        db_conn = Utils.create_db_conn()
        db_conn.write_all(sql_update)

    @staticmethod
    def validate_user_from_telegram(user: types.User) -> None:
        """
        Checks if user has previous records in Database and stores any parameter changes.

        :param user: Telegram user from message or query.
        """
        telegram_user = User.get_user_from_telegram_user(user)
        db_user = User.get_user_from_db(user.id)
        if db_user:
            if db_user != telegram_user:
                telegram_user.update()
        else:
            telegram_user.store()
