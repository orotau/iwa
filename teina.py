'''
The purpose of this module is to tie entries / sub-entries
to the tauria given.

For example
"kōkopu ruwao" is a sub-entry and the example is
" . . . aku kōkopu rūwao kua riro atu nei i te iwi."

There is a difference "ruwao" vs "rūwao"
It could be a mistake but to stop me questioning Te Haumihiata
all the time, I will search for "kōkopu rūwao" as well as "kōkopu ruwao"
and amalgamate the results
'''

TAUIRA_FILE_ID = 'hpk_tauira'

teina = {}

teina[TAUIRA_FILE_ID] = ([
    ("ahi whakamatiti", ["ahi o te whakamatiti"]),
    ("aiā", ["āiā"]),  
    ("ara tamatāne", ["ara tama tāne"]),
    ("e ai . . .", ["e ai"]),
    ("e ai ki . . .", ["e ai ki"]),
    ("E koe (E koe e koe)", ["E koe e koe", "E koe"]),
    ("He meka, he meka", ["He meka! He meka!"]),
    ("hohou (i te) rongo", ["hohou te rongo"]),
    ("huruhuru ngā raho", ["huruhuru rā anō ngā raho"]),
    ("ka mahi . . .", ["ka mahi"]),
    ("kānga kōpiro", ["kānga kopiro"]),
    ("kauae raro", ["kauaeraro"]),
    ("kauae runga", ["kauaerunga"]),
    ("kawititanga o te ringa(ringa)", ["kawititanga o te ringa", \
                                       "kawititanga o te ringaringa"]),
    ("kīhai ki . . .", ["kīhai ki"]),
    ("kino ngā piropiro", ["kino nā ngā piropiro"]),
    ("kōkopu ruwao", ["kōkopu rūwao"]),
    ("kuku o te manawa", ["kuku o tōna manawa"]),
    ("mataono (rite)", ["mataono rite", "mataono"]),
    ("matua whāngai", ["mātua whāngai"]),
    ("pai ngā piropiro", ["pai anō ngā piropiro"]),
    ("pōtaka kōtore rua", ["pōtaka kotore rua"]),
    ("puta te ihu", ["puta ai te ihu"]),
    ("tahi (i te) tahua", ["tahi te tahua"]),
    ("takahi (i te) whare", ["takahi whare"]),
    ("tama tu ki roto", ["tama tū ki roto"]),
    ("tangata whenua", ["tāngata whenua"]),
    ("tātai aro rangi", ["tātai arorangi"]),
    ("tau o te ate", ["tau o taku ate"]),
    ("tū atu, tū mai", ["tū atu tū mai"]),
    ("tūmatarehurehu", ["Tūmata-rehurehu"]),
    ("waha huka", ["wahahuka"]),
    ("whāngai hau", ["whāngaia te hau"]),
    ("whawhai kōpūtahi", ["riri kōpūtahi"]),
    ("whetūmārama", ["whetū mārama"]),
    ])
