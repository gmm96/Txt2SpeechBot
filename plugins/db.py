# -*- coding: utf-8 -*-
# @Author: gmm96

import MySQLdb
from plugins.shared import *

def read_db(query):
    global DB
    # Open database connection
    db = MySQLdb.connect(DB[0], DB[1], DB[2], DB[3])

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    try:
        # Execute the SQL command
        rows_count = cursor.execute(query)

        if rows_count > 0:
            # Fetch all the rows in a list of lists.
            results = cursor.fetchall()
        else:
            results = None

        return results
    except:
        print "Error: unable to fecth data"
        return [[]]

    # disconnect from server
    db.close()



def insert_db(query):
    global DB
    # Open database connection
    db = MySQLdb.connect(DB[0], DB[1], DB[2], DB[3])

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    try:
        # Execute the SQL command
        cursor.execute(query)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    db.close()



def update_db(query):
    global DB
    # Open database connection
    db = MySQLdb.connect(DB[0], DB[1], DB[2], DB[3])

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    try:
        # Execute the SQL command
        cursor.execute(query)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    db.close()

