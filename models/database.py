#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mysql.connector as MySQLdb
from mysql.connector.errors import Error as MySQLdbError
from typing import Optional, List, Tuple, Union
from models.constants import Constants


class Database:

    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.database = database
        self.connection = None
        self.connect_to_db(password)

    def __del__(self):
        self.disconnect_from_db()

    def connect_to_db(self, password) -> None:
        try:
            if not self.connection or self.connection.is_closed():
                self.connection = MySQLdb.connect(host=self.host, user=self.user, password=password, database=self.database)
        except MySQLdbError as e:
            exc_info = Constants.ExceptionMessages.DB_UNCONNECTED + str(e)
            Constants.STATUS_LOG.logger.error(exc_info)

    def disconnect_from_db(self) -> None:
        self.connection.close()

    def read_all(self, read_query: str) -> List[Tuple]:
        self.test_connection_and_reconnect_if_necessary()
        cursor = self.connection.cursor(buffered=True)
        try:
            cursor.execute(read_query)
            result = cursor.fetchall()
            return result
        except MySQLdbError as e:
            exc_info = Constants.ExceptionMessages.DB_READ + read_query + "\n" + str(e)
            Constants.STATUS_LOG.logger.exception(exc_info)
            return []
        finally:
            if cursor:
                cursor.close()

    def read_one(self, read_query: str) -> Optional[Tuple]:
        self.test_connection_and_reconnect_if_necessary()
        cursor = self.connection.cursor(buffered=True)
        try:
            cursor.execute(read_query)
            result = cursor.fetchone()
            return result
        except MySQLdbError as e:
            exc_info = Constants.ExceptionMessages.DB_READ + read_query + "\n" + str(e)
            Constants.STATUS_LOG.logger.exception(exc_info)
            return None
        finally:
            if cursor:
                cursor.close()

    def write_all(self, write_query: str) -> Union[int, bool]:
        self.test_connection_and_reconnect_if_necessary()
        cursor = self.connection.cursor(buffered=True)
        try:
            cursor.execute(write_query)
            self.connection.commit()
            return cursor.rowcount
        except MySQLdbError as e:
            if self.connection.is_connected():
                self.connection.rollback()
            exc_info = Constants.ExceptionMessages.DB_WRITE + write_query + "\n" + str(e)
            Constants.STATUS_LOG.logger.exception(exc_info)
            return False
        finally:
            if cursor:
                cursor.close()

    def test_connection_and_reconnect_if_necessary(self):
        if not self.connection or self.connection.is_closed():
            try:
                self.connection.ping(reconnect=True, attempts=5, delay=0)
            except MySQLdbError as e:
                exc_info = Constants.ExceptionMessages.DB_UNCONNECTED + str(e)
                Constants.STATUS_LOG.logger.error(exc_info)
