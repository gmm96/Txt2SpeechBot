# -*- coding: utf-8 -*-
# @Author: gmm96

import telebot  # API bot library
from telebot import types  # API bot types
import sys
import os
sys.path.append( os.path.dirname( os.getcwd( ) ) )
from plugins.file_processing import *
from plugins.shared import *
from collections import OrderedDict
import uuid
from alphabet_detector import AlphabetDetector
from rfc3986 import normalize_uri
import string


def replace_problematic_chars ( query ):
    global PROBLEMATIC_CHARS
    text = query.query
    for old_char, new_char in PROBLEMATIC_CHARS.items( ):
        text = text.replace( old_char, new_char )
    return text


def store_query ( query ):
    global QUERIES
    text = query
    code_id = str( uuid.uuid4( ) )
    # bot.send_message(6216877, 'queries id: ' + code_id)

    if len( QUERIES ) >= MAX_QUERIES:
        QUERIES.pop( QUERIES.iterkeys( ).next( ) )

    QUERIES[ code_id ] = text
    write_file( 'json', 'data/queries.json', QUERIES )
    return code_id


def isArabic ( s ):
    ad = AlphabetDetector( )
    string_without_numbers = str( s ).translate( None, string.digits )
    if string_without_numbers == '':
        return False
    else:
        return ad.only_alphabet_chars( unicode( string_without_numbers ), 'ARABIC' )


def normalize_text ( text ):
    if not isArabic( text ):
        return text.replace( ' ', '+' )
    else:
        return normalize_uri( text )
