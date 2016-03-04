'''
This file post-processes the text file.
Doing mainly 2 things

1) Some basic checks
2) Counts

'''

import config
import pickle
import os
from collections import namedtuple, Counter
import pprint
import teina
import maoriword as mw

Text_Chunk = namedtuple('Text_Chunk', 'text_chunk start end type')
word_types = ["oc", "voc", "moc", "icncw", "iccw", "ilcncw"]
conflations_for_count = [("te", ["Te"]), ("ngā", ["Ngā"]), ("e", ["E"])]

# the stop words don't survive the sort process as they are not classed
# as Māori words. This could be improved upon.
# For example finding a way of including 'Whina Cooper' in the sort
# for example. Need to think about sorting a mix of Māori and non-Māori terms
stop_words = ["k", "t", "p", "s", "w", "r", "g", "c" , "m", "h", "T", "n", \
              "rattus", "wh", "Kuīni Salote", "Pitt", "Tagata Pasifika", \
              "gastropoda", "downes", "q", "Taiwan", "C", "ng", \
              "Dalai Lama", "x", "Ātirīkona Samuel Williams", "Marble Arch", \
              "Himalaya", "Francis", "z", "etc", "wok", "Kānara Henry Despard", \
              "Rubik", "bacillus", "Kiribati", "St Pierre", "Whina Cooper", \
              "kss", "wasabi", "Mairatea Pitt-Pōrutu", "boomerang", \
              "Tana Umaga", "Chas", "Mollusca", \
             ]

def get_count_sort_key(count_and_word):
    '''
    The key for the sort data which is a list of tuples
    (count, word)
    The count is returned as a negative number so that the sorted data
    starts with the high counts and goes down to the low counts
    rather than starting at 1 and going upwards.    
    '''
    return -count_and_word[0], mw.get_list_sort_key(count_and_word[1])

def get_words_and_counts(file_id):

    PICKLE_EXTENSION = "p"

    cf = config.ConfigFile()
    pickle_files_path = (cf.configfile[cf.computername]['iwa_path'])
    pickle_file_path = pickle_files_path + file_id + os.extsep + PICKLE_EXTENSION

    with open(pickle_file_path, 'rb') as pickle_file:
        file_to_process = pickle.load(pickle_file)

    words = []
    for k, v in file_to_process.items():
        for Text_Chunk in v:
            if Text_Chunk.type in word_types:
                if Text_Chunk.text_chunk not in stop_words:                    
                    words.append(Text_Chunk.text_chunk)

    # the words for count are adjusted in 2 ways
    # a) From the teina - we amalgamate all the little brothers
    #    under the big brother
    # b) From the conflations_for_count

    words_for_count = words
    for index, word in enumerate(words_for_count):
        for big_brother, little_brothers in teina.teina[file_id]:
            for little_brother in little_brothers:
                if word == little_brother:
                    words_for_count[index] = big_brother

    for index, word in enumerate(words_for_count):
        for big_brother, little_brothers in conflations_for_count:
            for little_brother in little_brothers:
                if word == little_brother:
                    words_for_count[index] = big_brother               

    most_common_words = Counter(words_for_count).most_common()
    counts_and_words = []
    
    for index, word_and_count in enumerate(most_common_words):
        counts_and_words.insert(index, (word_and_count[1], word_and_count[0]))

    counts_and_words = sorted(counts_and_words, key=get_count_sort_key)
    words_and_counts = [tuple(reversed(x)) for x in counts_and_words]
    return words_and_counts   


if __name__ == '__main__':

    import sys
    import argparse
    import ast

    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # create the parser for the get_all_entries function
    get_words_and_counts_parser = subparsers.add_parser('get_words_and_counts')
    get_words_and_counts_parser.add_argument('file_id', choices = ['hpk_tauira',])
    get_words_and_counts_parser.set_defaults(function = get_words_and_counts)

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
