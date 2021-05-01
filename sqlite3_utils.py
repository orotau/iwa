'''
populate the Postgresql table
with the words
'''
# import psycopg2
import sqlite3
import json
# import xlrd
import config
import post_process_text_file
import difficulty_level
from collections import namedtuple

Text_Chunk = namedtuple('Text_Chunk', 'text_chunk start end type')

def get_sqlite3_connection():
    cf = config.ConfigFile()
    sql_db_path = cf.configfile[cf.computername]['sqlite3_db_path']
    con = sqlite3.connect(sql_db_path)
    return con


def populate_word():

    # get the word list
    cf = config.ConfigFile()
    iwa_path = (cf.configfile[cf.computername]['iwa_path'])
    json_filename = "all_words_for_iwa.json"
    full_json_path = iwa_path + json_filename
    
    # create the sqlite table 'word'
    sqlite3_connection = get_sqlite3_connection()
    cur = sqlite3_connection.cursor() 
    cur.execute('''CREATE TABLE IF NOT EXISTS 
                           word (word TEXT PRIMARY KEY)''')  
        
    with open(full_json_path, 'r') as f:
        unique_word_forms = json.load(f)
        # Need list of tuples for the executemany syntax
        unique_word_forms = [(x,) for x in unique_word_forms]
        cur.executemany("INSERT INTO word values (?)", unique_word_forms)
        sqlite3_connection.commit()
            
    sqlite3_connection.close()


def populate_waf():

    TAUIRA_FILE_ID = "hpk_tauira"

    # get the data
    words_and_frequency = post_process_text_file.get_words_and_counts(TAUIRA_FILE_ID)
    
    # create the sqlite table 'waf' - words and frequencies
    sqlite3_connection = get_sqlite3_connection()
    cur = sqlite3_connection.cursor() 
    cur.execute('''CREATE TABLE IF NOT EXISTS 
                           waf (word TEXT PRIMARY KEY, frequency INTEGER)''')  
        
    # Need list of tuples for the executemany syntax
    words_and_frequency = [tuple(x) for x in words_and_frequency]
    cur.executemany("INSERT INTO waf values (?, ?)", words_and_frequency)
    sqlite3_connection.commit()            
    sqlite3_connection.close()
    


def populate_board():

    # get the data
    boards = difficulty_level.distribute_children()

    # create the table
    sqlite3_connection = get_sqlite3_connection()
    cur = sqlite3_connection.cursor() 
    cur.execute('''CREATE TABLE IF NOT EXISTS 
                           board (word TEXT, letter TEXT, UNIQUE(word, letter))''') 

    # Need list of tuples for the executemany syntax
    boards = [tuple(x) for x in boards]
    cur.executemany("INSERT INTO board values (?, ?)", boards)
    sqlite3_connection.commit()            
    sqlite3_connection.close()


if __name__ == '__main__':

    import sys
    import argparse
    import ast

    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # create the parser for the populate_word function
    populate_word_parser = subparsers.add_parser('populate_word')
    populate_word_parser.set_defaults(function=populate_word)

    # create the parser for the populate_waf function
    populate_waf_parser = subparsers.add_parser('populate_waf')
    populate_waf_parser.set_defaults(function=populate_waf)

    # create the parser for the populate_board function
    populate_board_parser = subparsers.add_parser('populate_board')
    populate_board_parser.set_defaults(function=populate_board)

    # parse the arguments
    arguments = parser.parse_args()
    arguments = vars(arguments)  # convert from Namespace to dict

    # attempt to extract and then remove the function entry
    try:
        function_to_call = arguments['function']
    except KeyError:
        print("You need a function name. Please type -h to get help")
        sys.exit()
    else:
        # remove the function entry
        del arguments['function']

    if arguments:
        # remove any entries that have a value of 'None'
        # We are *assuming* that these are optional
        # We are doing this because we want the function definition to define
        # the defaults (NOT the function call)
        arguments = {k: v for k, v in arguments.items() if v is not None}

        # alter any string 'True' or 'False' to bools
        arguments = {k: ast.literal_eval(v) if v in ['True', 'False'] else v
                     for k, v in arguments.items()}

    result = function_to_call(**arguments)
    # note **arguments works fine for empty dict {}
