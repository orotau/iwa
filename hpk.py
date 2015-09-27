'''
Stuff specific to HPK
'''

end_dash = '-'
start_dash = '-'
ellipsis = ' . . .'
kotrr = 'kawititanga o te ringa(ringa)'
ekekek = 'E koe (E koe e koe)'
titt = 'tahi (i te) tahua'
titw = 'takahi (i te) whare'
hitr = 'hohou (i te) rongo'
mr = 'mataono (rite)'
en_dot = 'E nge.'


def clean_hpk_word_for_sorting(word_form):
    # if we have a suffix remove the - at the end of it
    if word_form.endswith(end_dash):
        word_form = word_form[:-1]

    # if we have a prefix remove the - at the start of it
    if word_form.startswith(start_dash):
        word_form = word_form[1:]

    # if we have a kīanga remove the ellipsis at the end of it
    if word_form.endswith(ellipsis):
        word_form = word_form[:-6]

    # if we have kawititanga o te ringa(ringa) remove the (ringa)
    if word_form == kotrr:
        word_form = word_form[:-7]

    # if we have E koe (E koe e koe) remove the  (E koe e koe)
    if word_form == ekekek:
        word_form = word_form[:-14]  # including the space before the bracket

    # if we have 'tahi (i te) tahua' remove the brackets
    if word_form == titt:
        word_form = word_form.replace('(', '').replace(')', '')

    # if we have 'takahi (i te) whare' remove the brackets
    if word_form == titw:
        word_form = word_form.replace('(', '').replace(')', '')

    # if we have 'hohou (i te) rongo' remove the brackets
    if word_form == hitr:
        word_form = word_form.replace('(', '').replace(')', '')

    # if we have 'mataono (rite)' remove the brackets
    if word_form == mr:
        word_form = word_form.replace('(', '').replace(')', '')

    # if we have 'E nge.' remove the . at the end of it
    if word_form == en_dot:
        word_form = word_form[:-1]

    return word_form
