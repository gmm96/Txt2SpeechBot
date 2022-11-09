# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing Utils class.
"""

import uuid
from telebot import types
from helpers.constants import Constants
from helpers.database import Database


class Utils:
    """
    Python class to perform basic operations with Telegram objects.
    """

    @staticmethod
    def create_db_conn() -> Database:
        """
        Create a Database object to connect to the application database.

        :return: Database object connection.
        :rtype: Database.
        """
        return Database(Constants.DB_CREDENTIALS[0], Constants.DB_CREDENTIALS[1],
                        Constants.DB_CREDENTIALS[2], Constants.DB_CREDENTIALS[3])

    @staticmethod
    def generate_unique_str() -> str:
        """
        Generates a random UUID.

        :return: Random identifier.
        :rtype: Str.
        """
        return str(uuid.uuid4())

    @staticmethod
    def record_message(msg: types.Message) -> None:
        """
        Records a message for logging purposes.

        :param msg: Telegram message.
        """
        if msg.content_type == 'text':
            if msg.chat.type == Constants.ChatType.PRIVATE:
                text = "%s (%s): %s" % (msg.from_user.username, str(msg.chat.id), msg.text)
            else:
                text = "%s (%s) in %s [%s]: %s" % (msg.from_user.username, str(msg.from_user.id), msg.chat.title,
                                                   str(msg.chat.id), msg.text)
            Constants.MSG_LOG.logger.info(text)

    @staticmethod
    def record_query(query: types.InlineQuery) -> None:
        """
        Records a query for logging purposes.

        :param query: Telegram inline query.
        """
        text = "%s (%s) %s" % (query.from_user.username, str(query.from_user.id), query.query)
        Constants.QRY_LOG.logger.info(text)
