'''
The functions to get the data ready for the web site
'''

import random
import json
import psycopg2
from collections import Counter
import maoriword as mw
import pū
import config
import pg_utils


# excluding those 9 letter words with
# 3 digraphs because they yield hardly
# any children and are a bit messy to
# put in the grid
nines_to_exclude = ('ngawhewhe',
                    'whāngongo',
                    'whewhengi',
                    'whiwhinga',
                    'whīwhiwhi')


def get_children(input_string, compulsory_letter, minimum_length=3):
    '''
    Returns a list containing all the word forms (children)
    that can be made from the input_string.

    The input string can be of one of two forms
    a) A Māori word
    b) A Koru

    If the latter then any digraphs on the last row need to be reversed.
    '''

    # if minimum length is passed as a string *try* and convert to integer
    minimum_length = int(minimum_length)

    children = []

    # if the input string contains any reversed digraphs, reverse them
    # note that this can only happen with a koru on the last line
    # these 2 are mutually exclusive and will not interfere with eachother

    # swap digraphs around if necessary
    if input_string[6] + input_string[5] in pū.digraphs:
        input_string = list(input_string)
        input_string[6], input_string[5] = input_string[5], input_string[6]
        input_string = ''.join(input_string)
    elif input_string[5] + input_string[4] in pū.digraphs:
        input_string = list(input_string)
        input_string[5], input_string[4] = input_string[4], input_string[5]
        input_string = ''.join(input_string)
    else:
        pass  # no action required as there are no reversed digraphs

    input_string_as_list = mw._aslist(input_string)

    # get the word list
    db_access_info = pg_utils.get_db_access_info()
    with psycopg2.connect(database=db_access_info[0],
                          user=db_access_info[1],
                          password=db_access_info[2]) as connection:

        with connection.cursor() as cursor:

            all_word_forms_query = "SELECT * FROM pgt_word"
            cursor.execute(all_word_forms_query)
            unique_word_forms = cursor.fetchall()  # list of tuples

    connection.close()

    # list of strings
    unique_word_forms = [''.join(x) for x in unique_word_forms]
    for word in [x for x in unique_word_forms if len(x) >= minimum_length]:

        word_as_list = mw._aslist(word)

        is_child = False
        if not (Counter(word_as_list) - Counter(input_string_as_list)):
            is_child = True

        if is_child and compulsory_letter in word_as_list:
            children.append(word)

    return(children)



def get_koru(seed_word, centre_letter=None):

    if seed_word in nines_to_exclude:
            return ValueError

    koru = [None] * 9  # initialise koru

    # listify the seed word and split into single letters and digraphs
    seed_word_as_list = mw._aslist(seed_word)

    # 'single_letters' and 'digraphs' will be emptied
    single_letters = [x for x in seed_word_as_list if
                      x in pū.all_single_letters]
    digraphs = [x for x in seed_word_as_list if x in pū.digraphs]
    digraphs_count = len(digraphs)

    if centre_letter is None:
        # randomly select 'centre letter'
        centre_letter = random.choice(single_letters)
    else:
        pass  # we are assuming we have a 'centre letter' that is in the word

    # remove it from single letters
    single_letters.remove(centre_letter)

    # add 'centre letter' to koru, 8 squares remaining to be filled
    koru[8] = centre_letter

    # randomly select and randomly place the digraphs (if any)
    # note there are constraints to the randomness
    if digraphs:
        # establish the squares where it is ok to put digraphs
        if centre_letter in pū.duals_left:  # w or n
            # avoid 'vertical digraphs'
            ok_digraph_squares = [(1, 2), (5, 4)]
        elif centre_letter in pū.duals_right:  # h
            # avoid 'vertical digraphs'
            ok_digraph_squares = [(0, 1), (6, 5)]
        else:
            # 'vertical digraphs' not an issue
            ok_digraph_squares = [(0, 1), (1, 2), (5, 4), (6, 5)]

        if digraphs_count == 1 or digraphs_count == 2:
            # randomly select 'digraph1' and remove it from digraphs
            digraph1 = random.choice(digraphs)
            digraphs.remove(digraph1)

            # randomly select the squares for 'digraph1'
            digraph1_squares = random.choice(ok_digraph_squares)

            # add 'digraph1' to koru
            koru[digraph1_squares[0]] = digraph1[0]  # 7 squares remaining
            koru[digraph1_squares[1]] = digraph1[1]  # 6 squares remaining

            if digraphs_count == 2:
                # select 'digraph2' and remove it from digraphs
                digraph2 = random.choice(digraphs)  # should only be 1 left
                digraphs.remove(digraph2)

                # place the 2nd digraph directly above or below the first
                if digraph1_squares == (0, 1):
                    digraph2_squares = (6, 5)
                if digraph1_squares == (6, 5):
                    digraph2_squares = (0, 1)
                if digraph1_squares == (1, 2):
                    digraph2_squares = (5, 4)
                if digraph1_squares == (5, 4):
                    digraph2_squares = (1, 2)

                # add 'digraph2 to koru'
                koru[digraph2_squares[0]] = digraph2[0]  # 5 squares remaining
                koru[digraph2_squares[1]] = digraph2[1]  # 4 squares remaining
    # End of Placing Digraphs

    # place the rest of the single letters (aside from that in the centre)
    if digraphs_count == 2:
            # 4 squares remaining
            # we may have 1 consonant to place in a specific position
            remaining_consonant = [x for x in single_letters if
                                   x in pū.consonants]
            if remaining_consonant:
                if digraph1_squares == (0, 1) or digraph1_squares == (6, 5):
                    koru[3] = remaining_consonant[0]
                else:
                    koru[7] = remaining_consonant[0]
                single_letters.remove(remaining_consonant[0])

            # randomly assign the remaining single letters
            # (should all be vowels)
            # 3 or 4 remaining
            for index, square in enumerate(koru):
                if square is None:
                    letter_to_place = random.choice(single_letters)
                    single_letters.remove(letter_to_place)
                    koru[index] = letter_to_place
    # DONE for 2 digraphs

    if digraphs_count == 1:
        # 6 letters remaining to place, of which at least 4 will be vowels

        # get *empty square on digraph row*
        if digraph1_squares == (0, 1):
            empty_square_on_digraph_row = 2
        if digraph1_squares == (1, 2):
            empty_square_on_digraph_row = 0
        if digraph1_squares == (6, 5):
            empty_square_on_digraph_row = 4
        if digraph1_squares == (5, 4):
            empty_square_on_digraph_row = 6

        # the *empty square on the digraph row* must have a vowel in it
        letter_to_place = random.choice([x for x in single_letters if
                                         x in pū.all_vowels])
        single_letters.remove(letter_to_place)
        koru[empty_square_on_digraph_row] = letter_to_place
        # 5 squares remaining

        # get *empty square underneath or above the digraph*
        if digraph1_squares == (0, 1):
            empty_square_underneath_or_above_the_digraph = 7
        if digraph1_squares == (1, 2):
            empty_square_underneath_or_above_the_digraph = 3
        if digraph1_squares == (6, 5):
            empty_square_underneath_or_above_the_digraph = 7
        if digraph1_squares == (5, 4):
            empty_square_underneath_or_above_the_digraph = 3

        # the *empty square underneath or above the digraph*
        # must have a vowel in it
        letter_to_place = random.choice([x for x in single_letters if
                                         x in pū.all_vowels])
        single_letters.remove(letter_to_place)
        koru[empty_square_underneath_or_above_the_digraph] = letter_to_place
        # 4 squares remaining

        # get the *empty square in the middle column*
        if digraph1_squares == (0, 1):
            empty_square_middle_column = 5
        if digraph1_squares == (1, 2):
            empty_square_middle_column = 5
        if digraph1_squares == (6, 5):
            empty_square_middle_column = 1
        if digraph1_squares == (5, 4):
            empty_square_middle_column = 1

        # the *empty square in the middle column* must have a vowel in it
        letter_to_place = random.choice([x for x in single_letters if
                                         x in pū.all_vowels])
        single_letters.remove(letter_to_place)
        koru[empty_square_middle_column] = letter_to_place
        # 3 squares remaining

    if digraphs_count == 1 and centre_letter in pū.consonants:
        # 3 squares remaining

        # get the *empty square in the middle row*
        if digraph1_squares == (0, 1):
            empty_square_middle_row = 3
        if digraph1_squares == (1, 2):
            empty_square_middle_row = 7
        if digraph1_squares == (6, 5):
            empty_square_middle_row = 3
        if digraph1_squares == (5, 4):
            empty_square_middle_row = 7

        # the *empty square in the middle row* must have a vowel in it
        letter_to_place = random.choice([x for x in single_letters if
                                         x in pū.all_vowels])
        single_letters.remove(letter_to_place)
        koru[empty_square_middle_row] = letter_to_place
        # 2 squares remaining

        # fill the remaining 2 squares with whatever letters remain
        for index, square in enumerate(koru):
            if square is None:
                letter_to_place = random.choice(single_letters)
                single_letters.remove(letter_to_place)
                koru[index] = letter_to_place

    if digraphs_count == 1 and centre_letter in pū.all_vowels:
        # 3 squares remaining (1 isolated and 2 vertically together)
        # 3C or 2C, 1V or 1C, 2V

        # mostly these will be 3 consonants and we just want to ensure that we
        # don't create any 'vertical digraphs'
        # and we want to keep vowels and consonants separate

        # get the *isolated empty square*
        if digraph1_squares == (0, 1):
            isolated_empty_square = 6
        if digraph1_squares == (1, 2):
            isolated_empty_square = 4
        if digraph1_squares == (6, 5):
            isolated_empty_square = 0
        if digraph1_squares == (5, 4):
            isolated_empty_square = 2

        # the *isolated empty square* must have a 'w' in it if we have one
        # otherwise a consonant
        if 'w' in single_letters:
            letter_to_place = 'w'
        else:
            letter_to_place = random.choice([x for x in single_letters if
                                             x in pū.consonants])

        single_letters.remove(letter_to_place)
        koru[isolated_empty_square] = letter_to_place
        # 2 squares remaining

        # get the *empty square in the middle row*
        if digraph1_squares == (0, 1):
            empty_square_middle_row = 3
        if digraph1_squares == (1, 2):
            empty_square_middle_row = 7
        if digraph1_squares == (6, 5):
            empty_square_middle_row = 3
        if digraph1_squares == (5, 4):
            empty_square_middle_row = 7

        # the *empty square in the middle row* must have a consonant in it if
        # we have one otherwise a vowel.
        try:
            letter_to_place = random.choice([x for x in single_letters if
                                             x in pū.consonants])
        except IndexError:
            # no consonants remaining
            letter_to_place = random.choice([x for x in single_letters if
                                             x in pū.all_vowels])

        single_letters.remove(letter_to_place)
        koru[empty_square_middle_row] = letter_to_place
        # 1 square remaining

        # fill the remaining square with whatever letter remains
        for index, square in enumerate(koru):
            if square is None:
                letter_to_place = random.choice(single_letters)
                single_letters.remove(letter_to_place)
                koru[index] = letter_to_place
    # DONE for 1 digraph

    if digraphs_count == 0:
        # no digraphs, so only the centre letter has been placed
        # we have 8 letters left to place
        if centre_letter in pū.all_vowels:
            vowel_first = True
        else:
            vowel_first = False
        for index, square in enumerate(koru[:-1]):
            if index % 2 == 0:  # 0, 2, 4, 6
                if vowel_first:
                    letter_to_place = random.choice(
                                      [x for x in single_letters
                                       if x in pū.all_vowels])
                else:
                    try:
                        letter_to_place = random.choice(
                                          [x for x in single_letters
                                           if x in pū.consonants])
                    except IndexError:
                        # no consonants remaining
                        letter_to_place = random.choice(
                                          [x for x in single_letters
                                           if x in pū.all_vowels])
            else:  # 1, 3, 5, 7
                if vowel_first:
                    try:
                        letter_to_place = random.choice(
                                          [x for x in single_letters
                                           if x in pū.consonants])
                    except IndexError:
                        # no consonants remaining
                        letter_to_place = random.choice(
                                          [x for x in single_letters
                                           if x in pū.all_vowels])
                else:
                    letter_to_place = random.choice([x for x in single_letters
                                                     if x in pū.all_vowels])
            single_letters.remove(letter_to_place)
            koru[index] = letter_to_place

    return ''.join(koru)
    # DONE for 0 digraphs


if __name__ == '__main__':

    import sys
    import argparse
    import ast

    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # create the parser for the get_children function
    get_children_parser = subparsers.add_parser('get_children')
    get_children_parser.add_argument('input_string')
    get_children_parser.add_argument('compulsory_letter')
    get_children_parser.add_argument('-minimum_length')
    get_children_parser.set_defaults(function=get_children)

    # create the parser for the get_all_children_counts function
    get_all_children_counts_parser = \
        subparsers.add_parser('get_all_children_counts')
    get_all_children_counts_parser.set_defaults(
        function=get_all_children_counts)

    # create the parser for the get_koru function
    get_koru_parser = subparsers.add_parser('get_koru')
    get_koru_parser.add_argument('-seed_word')
    get_koru_parser.set_defaults(function=get_koru)

    # parse the arguments
    arguments = parser.parse_args()
    arguments = vars(arguments)  # convert from Namespace to dict

    # attempt to extract and then remove the function entry
    try:
        function_to_call = arguments['function']
    except KeyError:
        # python pangakupu.py entered on command line
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
    print(result)
