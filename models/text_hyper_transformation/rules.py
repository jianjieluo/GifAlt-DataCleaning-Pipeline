"""
Handmade lists or dicts as rules used in `hypernymizer.py`
"""

################# Group Spacy NER Classes ###################
"""
Spacy Named Entity Recognition class:
https://spacy.io/api/annotation#named-entities

PERSON	    People, including fictional.
NORP	    Nationalities or religious or political groups.
FAC	        Buildings, airports, highways, bridges, etc.
ORG	        Companies, agencies, institutions, etc.
GPE	        Countries, cities, states.
LOC	        Non-GPE locations, mountain ranges, bodies of water.
PRODUCT	    Objects, vehicles, foods, etc. (Not services.)
EVENT	    Named hurricanes, battles, wars, sports events, etc.
WORK_OF_ART	Titles of books, songs, etc.
LAW	        Named documents made into laws.
LANGUAGE	Any named language.
DATE	    Absolute or relative dates or periods.
TIME	    Times smaller than a day.
PERCENT	    Percentage, including ”%“.
MONEY	    Monetary values, including unit.
QUANTITY	Measurements, as of weight or distance.
ORDINAL	    “first”, “second”, etc.
CARDINAL	Numerals that do not fall under another type.
"""

REPLACE_CLASSES = [
    "PERSON"
]

DROP_CLASSES = [
    "NORP",
    "ORG",
    "GPE",
    "WORK_OF_ART",
    "DATE",
    "TIME",
    "PERCENT",
    "MONEY",
    "QUANTITY",
    "CARDINAL",
    "EVENT",
    "FAC",
    "LOC",
    "PRODUCT",
    "LAW",
    "LANGUAGE",
    "ORDINAL"
]

################# Predefined useless words ###################
MONTH = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]