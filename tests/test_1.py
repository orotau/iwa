import maoriword as mw
import pytest

def test_leading_and_or_trailing_whitespace():
    with pytest.raises(ValueError):
        mw.MaoriWord('  mana') #leading
        mw.MaoriWord('  mana    ') #leading and trailing
        mw.MaoriWord('mana  ') # trailing


def test_whitespace_or_empty():
    with pytest.raises(ValueError):
        mw.MaoriWord('') #empty
        mw.MaoriWord('      ') #whitespace


def test_word_as_list():
    #check the aslist method that converts the word to a list that allows for digraphs
    assert mw._aslist('mana') == list('mana') #should perform identically to list when no digraphs
    assert mw._aslist('ngutu') != list('ngutu')
    assert mw._aslist('ngutu') == ['ng','u','t','u']
    assert mw._aslist('whakangaro') == ['wh', 'a', 'k', 'a', 'ng', 'a', 'r', 'o']
    assert mw._aslist('WhĀnGa') == ['Wh', 'Ā', 'nG', 'a']
    assert mw._aslist('awe awe') == list('awe awe')


def test_all_legal_characters():
    #check the method that checks that the word consists of legal characters only
    assert mw._isalllegalletters('aeiou') == True
    assert mw._isalllegalletters('whakangākau') == True
    assert mw._isalllegalletters('wakangākau') == True #missing h but all legal characters
    assert mw._isalllegalletters('x') == False
    assert mw._isalllegalletters('whakagākau') == False  #missed the 'n' leaving 'g' which is illegal


def test_word_split():
    assert mw._word_split('awe awe') == ['awe','awe']
    assert mw._word_split('a-ahi') == ['a','ahi']
    assert mw._word_split('a- ahi') == ['a', '', 'ahi'] #repeated separators


def test_words_split():
    assert mw._words_split('Āe, āe') == ['Āe', 'āe']

def test_ends_in_vowel():
    assert mw._endsinvowel('awe') == True
    assert mw._endsinvowel('ā') == True
    assert mw._endsinvowel('huhy') == False


def test_is_consonant_vowel():
    assert mw._isconsonantvowel('awe') == True
    assert mw._isconsonantvowel('awe ') == False
    assert mw._isconsonantvowel('whanau') == True
    assert mw._isconsonantvowel('WHANGAREI') == True


def test_initialisation():
    assert mw.MaoriWord('utu').word == 'utu'
    assert mw.MaoriWord('Korekore-piri-ki-ngā-Tangaroa').word == 'Korekore-piri-ki-ngā-Tangaroa'
    assert mw.MaoriWord('āēīōĀĒĪŌŪ').word == 'āēīōĀĒĪŌŪ'
    with pytest.raises(ValueError):
        mw.MaoriWord('x')
        mw.MaoriWord('whakagākau') #missed the 'n' leaving 'g' which is illegal
        mw.MaoriWord('a- ahi') #repeated separators
        mw.MaoriWord('huhy')


def test_remove_intra_word_punctuation():
    assert mw._remove_intra_word_punctuation('awe awe') == 'aweawe'
    assert mw._remove_intra_word_punctuation('awe-awe') == 'aweawe'


def test_demacronise():
    assert mw._demacronise('no change') == 'no change'
    assert mw._demacronise('āēīōūĀĒĪŌŪ') == 'aeiouAEIOU'


def test_get_list_sort_key():
    assert mw.get_list_sort_key('rā') == (['r', 'a'], ['r', 'ā'], ['r', 'ā'])
    assert mw.get_list_sort_key('NGĀ') == (['ng', 'a'], ['ng', 'ā'], ['NG', 'Ā'])


def test_list_sorting():
    from random import shuffle

    #Test ONLY ascending sorts

    #at the most basic level macronised vowels are treated as unmacronised
    basic_group = ['aroha', 'ēhea', 'hauiti'] #the correct ascending order
    shuffle(basic_group)
    basic_group_shuffled = basic_group
    assert sorted(basic_group_shuffled, key=mw.get_list_sort_key) == ['aroha', 'ēhea', 'hauiti']
    assert sorted(basic_group_shuffled, key=mw.get_list_sort_key) != sorted(basic_group_shuffled)

    #the sort will disregard any dash(es)
    dash_group = ['takini', 'Taki-o-Autahi', 'Takirā'] #the correct ascending order
    shuffle(dash_group)
    dash_group_shuffled = dash_group
    assert sorted(dash_group_shuffled, key=mw.get_list_sort_key) == ['takini', 'Taki-o-Autahi', 'Takirā']
    #dash sorts before letters asciibetically
    assert sorted(dash_group_shuffled, key=mw.get_list_sort_key) != sorted(dash_group_shuffled)

    #the sort will disregard any space(s)
    space_group = ['tuturuatu', 'tuturu pourewa', 'tuturuwhatu'] #the correct ascending order
    shuffle(space_group)
    space_group_shuffled = space_group
    assert sorted(space_group_shuffled, key=mw.get_list_sort_key) == ['tuturuatu', 'tuturu pourewa', 'tuturuwhatu']
    #space sorts before letters asciibetically
    assert sorted(space_group_shuffled, key=mw.get_list_sort_key) != sorted(space_group_shuffled)

    #order when words differ only by macron
    kaka4 = ['kaka', 'kakā', 'kāka', 'kākā'] #the correct ascending order
    shuffle(kaka4)
    kaka4_shuffled = kaka4
    assert sorted(kaka4_shuffled, key=mw.get_list_sort_key) == ['kaka', 'kakā', 'kāka', 'kākā']

    #order for digraph 'ng'
    digraph_ng_3 = ['tunehe', 'tunu', 'tunga'] #the correct ascending order
    shuffle(digraph_ng_3)
    digraph_ng_3_shuffled = digraph_ng_3
    assert sorted(digraph_ng_3_shuffled, key=mw.get_list_sort_key) == ['tunehe', 'tunu', 'tunga']
    assert sorted(digraph_ng_3_shuffled, key=mw.get_list_sort_key) != sorted(digraph_ng_3_shuffled)

    #order for digraph 'wh'
    digraph_wh_3 = ['kawe', 'kawiti', 'kawhe'] #the correct ascending order
    shuffle(digraph_wh_3)
    digraph_wh_3_shuffled = digraph_wh_3
    assert sorted(digraph_wh_3_shuffled, key=mw.get_list_sort_key) == ['kawe', 'kawiti', 'kawhe']
    assert sorted(digraph_wh_3_shuffled, key=mw.get_list_sort_key) != sorted(digraph_wh_3_shuffled)

    #order when words differ only by case
    assert sorted(['kahurangi','Kahurangi'], key=mw.get_list_sort_key) == ['Kahurangi', 'kahurangi']
    assert sorted(['Kahurangi','kahurangi'], key=mw.get_list_sort_key) == ['Kahurangi', 'kahurangi']

    #the one identifiable difference with HPK
    assert sorted(['Tāne', 'tane', 'tāne'], key=mw.get_list_sort_key) == ['tane', 'Tāne', 'tāne']
