'''
This module establishes is used to introduce a 'difficulty level'
for each board, as follows

a) First get a frequency score for each child word
for a board where a board is defined by '9 letter word" + "compulary letter"
'''    

# excluding those 9 letter words with
# 3 digraphs because they yield hardly
# any children and are a bit messy to
# put in the grid

import config
# import psycopg2
import maoriword as mw
import pprint
import json
import pangakupu as pk
import boards_and_children
import sqlite3_utils

# These numbers are educated guesses at a first go
# of something that seems ok
MINIMUM_GROUP_SIZE = 4
PAI_MINIMUM_FREQUENCY = 24
TINO_PAI_MINIMUM_FREQUENCY = 4
TINO_PAI_RAWA_ATU_MINIMUM_FREQUENCY = 0
VERY_LARGE_NUMBER = 100000

def distribute_children():
    '''
    For each word, middle letter combination (board)
    distribute the child words into groups according to frequency

    and then remove those boards that don't have 'enough'
    in any of the 3 groups
    '''

    # get the word frequency data
    sqlite3_connection = sqlite3_utils.get_sqlite3_connection()
    cur = sqlite3_connection.cursor()
    
    word_frequency_pairs = []

    cur.execute("SELECT * FROM waf")
    word_frequency_pairs = cur.fetchall()  # list of tuples
    sqlite3_connection.close()
    words = [x[0] for x in word_frequency_pairs]

    boards = []
    for k, v in boards_and_children.boards_and_children.items():
        child_word_frequencies = []
        for child_word in v:
            try:
                child_word_index = words.index(child_word)
            except ValueError:
                # the headword in the dictionary doesn't appear
                # anywhere in the example text
                child_word_score = 0
            else:
                child_word_score = word_frequency_pairs[child_word_index][1]

            child_word_frequencies.append(child_word_score)

        intervals = [frozenset(range(PAI_MINIMUM_FREQUENCY, VERY_LARGE_NUMBER)), \
                     frozenset(range(TINO_PAI_MINIMUM_FREQUENCY, PAI_MINIMUM_FREQUENCY)), \
                     frozenset(range(TINO_PAI_RAWA_ATU_MINIMUM_FREQUENCY, \
                                     TINO_PAI_MINIMUM_FREQUENCY))]
        counts = [0] * len(intervals)

        for n in sorted(child_word_frequencies):
          for i, inter in enumerate(intervals):
            if n in inter:
              counts[i] += 1

        if not(counts[0] < MINIMUM_GROUP_SIZE or 
               counts[1] < MINIMUM_GROUP_SIZE or 
               counts[2] < MINIMUM_GROUP_SIZE):
            boards.append(k) 
    return boards

def group_children(children):
    '''
    This function takes a list of  children and sorts them into
    three lists of tuples (word, frequency)
    - pai
    - tino pai
    - tino pai rawa atu
    '''
    # get the word frequency data
    sqlite3_connection = sqlite3_utils.get_sqlite3_connection()
    cur = sqlite3_connection.cursor()

    word_frequency_pairs = []
    for child in children:

        cur.execute("SELECT frequency FROM waf WHERE word=?", (child,))

        frequency = cur.fetchall()  # list of 1 tuple (assumed)

        if frequency == []:
            # child word not found in word frequency list
            frequency_to_use = 0
        else:
            frequency_to_use = int(frequency[0][0])
        word_frequency_pairs.append((child, frequency_to_use))

    sqlite3_connection.close()
    
    intervals = [frozenset(range(PAI_MINIMUM_FREQUENCY, VERY_LARGE_NUMBER)), \
         frozenset(range(TINO_PAI_MINIMUM_FREQUENCY, PAI_MINIMUM_FREQUENCY)), \
         frozenset(range(TINO_PAI_RAWA_ATU_MINIMUM_FREQUENCY, \
                         TINO_PAI_MINIMUM_FREQUENCY))]

    pai = []
    tino_pai = []
    tino_pai_rawa_atu = []

    for word, frequency in word_frequency_pairs:
        if frequency in intervals[0]:
            pai.append((word, frequency))
        elif frequency in intervals[1]:
            tino_pai.append((word, frequency))
        elif frequency in intervals[2]:
            tino_pai_rawa_atu.append((word, frequency))
        else:
            raise
    return pai, tino_pai, tino_pai_rawa_atu    

if __name__ == '__main__':

    import sys
    import argparse
    import ast

    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # create the parser for the get_average_score function
    distribute_children_parser = subparsers.add_parser \
    ('distribute_children')
    distribute_children_parser.set_defaults \
    (function = distribute_children)

    # parse the arguments
    arguments = parser.parse_args()
    arguments = vars(arguments) #convert from Namespace to dict

    #attempt to extract and then remove the function entry
    try:
        function_to_call = arguments['function'] 
    except KeyError:
        print ("You need a function name. Please type -h to get help")
        sys.exit()
    else:
        #remove the function entry as we are only passing arguments
        del arguments['function']
    
    if arguments:
        #remove any entries that have a value of 'None'
        #We are *assuming* that these are optional
        #We are doing this because we want the function definition to define
        #the defaults (NOT the function call)
        arguments = { k : v for k,v in arguments.items() if v is not None }

        #alter any string 'True' or 'False' to bools
        arguments = { k : ast.literal_eval(v) if v in ['True','False'] else v 
                                              for k,v in arguments.items() }       

    result = function_to_call(**arguments) #note **arguments works fine for empty dict {}
   
    print (result)

