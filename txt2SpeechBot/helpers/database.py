# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File containing Database class.
"""

import re
import mysql.connector as mysqldb
from mysql.connector.errors import Error as MySQLdbError
from typing import Optional, List, Tuple, Union
from helpers.constants import Constants


class Database:
    """
    Python class to perform a different set of operations in a MySQL Database.

    This class provides a simpler way to interact with application database than the common python
    MySQL connectors. The connection is done as soon as you create an instance, but cursors are
    created in every method to avoid errors (such as cursor disconnection, trying to perform more
    that one operation at the same time, etc). It also deals with instance deleting, lost connection
    and provides a method to prepare a string for database.
    """

    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        """
        Opens a connection to a MySQL Database system prepared to work.

        :param host: Host address to Database machine.
        :param user: Username used for login in Database system.
        :param password: Password used for login in Database system.
        :param database: Database where the connection will point.
        """
        self.host: str = host
        self.user: str = user
        self.database: str = database
        self.connection: Optional[mysqldb.MySQLConnection] = None
        self.connect_to_db(password)

    def __del__(self) -> None:
        """
        Closes a Database connection when the object is moved to the garbage collector.
        """
        self.disconnect_from_db()

    def connect_to_db(self, password: str) -> None:
        """
        Tries to connect to a specific Database is connections is not already done.

        :param password: Password used for login in Database system.
        """
        try:
            if not self.connection or self.connection.is_closed():
                self.connection = mysqldb.connect(host=self.host, user=self.user,
                                                  password=password, database=self.database)
        except MySQLdbError:
            Constants.STA_LOG.logger.error(Constants.ExceptionMessages.DB_UNCONNECTED, exc_info=True)

    def disconnect_from_db(self) -> None:
        """
        Closes a Database connection.
        """
        self.connection.close()

    def read_all(self, read_query: str) -> List[Tuple]:
        """
        Executes a read operation and returns all rows of a query result set.

        :param read_query: MySQL read statement.
        :return: Query result set from execution of a MySQL statement.
        :rtype: List[tuple] or empty list[].
        """
        self.test_connection_and_reconnect_if_necessary()
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(read_query)
            result = cursor.fetchall()
            return result
        except MySQLdbError:
            Constants.STA_LOG.logger.exception(Constants.ExceptionMessages.DB_READ + read_query, exc_info=True)
            return []
        finally:
            if cursor:
                cursor.close()

    def read_one(self, read_query: str) -> Optional[Tuple]:
        """
        Executes a read operation and returns just one row of the query result set.

        :param read_query: MySQL read statement.
        :return: Query result row from execution of a MySQL statement.
        :rtype: Tuple[] or None.
        """
        self.test_connection_and_reconnect_if_necessary()
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(read_query)
            result = cursor.fetchone()
            return result
        except MySQLdbError:
            Constants.STA_LOG.logger.exception(Constants.ExceptionMessages.DB_READ + read_query, exc_info=True)
            return None
        finally:
            if cursor:
                cursor.close()

    def write_all(self, write_query: str) -> Union[int, bool]:
        """
        Executes an insert or update operation and returns the number of modified rows or False if
        the operation does not change anything.

        :param write_query: MySQL insert or update statement.
        :return: Number of modified rows or False if no changes were done.
        :rtype: Int or bool.
        """
        self.test_connection_and_reconnect_if_necessary()
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(write_query)
            self.connection.commit()
            return cursor.rowcount
        except MySQLdbError:
            if self.connection.is_connected():
                self.connection.rollback()
            Constants.STA_LOG.logger.exception(Constants.ExceptionMessages.DB_WRITE + write_query, exc_info=True)
            return False
        finally:
            if cursor:
                cursor.close()

    def test_connection_and_reconnect_if_necessary(self) -> None:
        """
        Tests if connection is available and reconnects if the connections has been lost.
        """
        if not self.connection or self.connection.is_closed():
            try:
                self.connection.ping(reconnect=True, attempts=5, delay=0)
            except MySQLdbError:
                Constants.STA_LOG.logger.error(Constants.ExceptionMessages.DB_UNCONNECTED, exc_info=True)

    @staticmethod
    def db_str(text: str) -> str:
        """
        Translates a string to make it compatible with the Database system.

        :param text: string to be translated
        :return: String prepared for Database manipulation.
        :rtype: Str.
        """
        if text:
            return re.sub('[^A-Za-z0-9ñ\s]+', '', text)
        else:
            return text or ''
