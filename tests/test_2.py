import pytest
from unicodedata import normalize
import pū
from collections import Counter
import config
import json
import maoriword as mw
import psycopg2

db_name = "pango"
db_user = "kereama"
db_pass = "heahatemeanui"

def test_pangakupu_words():

    with psycopg2.connect(database = db_name, 
                          user = db_user, 
                          password = db_pass) as connection:

        with connection.cursor() as cursor:

            all_word_forms_query = "SELECT * FROM pgt_word"
            cursor.execute(all_word_forms_query)
            unique_word_forms = cursor.fetchall() #list of tuples
 
    connection.close()
    all_words_for_iwa = [''.join(x) for x in unique_word_forms] #list of strings

    #word counts
    assert len(all_words_for_iwa) == 11601
    c = Counter(len(x) for x in all_words_for_iwa)
    assert dict(c) == {1: 9,
                       2: 57,
                       3: 255,
                       4: 1099,
                       5: 1169,
                       6: 2691,
                       7: 1568,
                       8: 1949,
                       9: 830,
                       10: 971,
                       11: 451,
                       12: 279,
                       13: 164,
                       14: 54,
                       15: 35,
                       16: 10,
                       17: 6,
                       18: 3,
                       19: 1}

    assert sum(dict(c).values()) == 11601 #recheck the count
    assert sum([k * v for k, v in dict(c).items()]) == 83080 #letter counts
    assert len(set(all_words_for_iwa)) == 11601 #test for uniqueness
    
    #check every entry is lower case
    assert [x if x.lower() == x else 'derp' for x in all_words_for_iwa] == all_words_for_iwa

    #check every entry is free of punctuation
    assert [x if mw._isalllegalletters(x) else 'derp' for x in all_words_for_iwa] == all_words_for_iwa

    #check that the basics for all maori words hold
    for x in all_words_for_iwa:
        assert x == mw.MaoriWord(x).word

    #letter counts
    all_letters_for_iwa = []
    for x in all_words_for_iwa:
        all_letters_for_iwa.extend(mw._aslist(x))
    c = dict(Counter(all_letters_for_iwa))
    assert c == {'a': 14894,
                 'ā': 2252,
                 'e': 5125,
                 'ē': 281,
                 'h': 3970,
                 'i': 6765,
                 'ī': 627,
                 'k': 6882,
                 'm': 2406,
                 'n': 2002,
                 'ng': 1834,
                 'o': 5521,
                 'ō': 1216,
                 'p': 3733,
                 'r': 6270,
                 't': 5880,
                 'u': 5736,
                 'ū': 993,
                 'w': 1245,
                 'wh': 1807}

    assert sum(dict(c).values()) == 79439 #digraphs count as 1 letter

    #cross check letter counts from words vs direct letter counts
    assert 83080 == 79439 + c['ng'] + c['wh'] #digraphs count as 2 letters
