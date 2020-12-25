# video caption domain cleaner
# stage == 4 --> candidates whose tags do not appear in predefined tag_refine list are discarded
# stage == 5 --> candidates contains predefined film, tv show, mv names etc are discarded
# stage == 6 --> clip predefined meaningless web-related boiler plate
#                discard predefined meaningless high freq sentences

import os
import re
import sys
import csv
import argparse
import string
import nltk
from nltk.corpus import stopwords, words
from nltk.stem import WordNetLemmatizer 
from models.base_cleaner import BaseCleaner
from models.profanities_filter import ProfanitiesFilter


class DomainCleaner(BaseCleaner):
    def __init__(self):
        super(DomainCleaner, self).__init__()
        self.stop_words = set(stopwords.words('english'))

        self.refine_tags = None
        self.stemmer = None
        self.filmetc_filter = None

        self.boiler_plate = None
        self.boiler_regex_plate = None
        self.black_sents = None

    def load_model(self, stage):
        if stage == 4:
            with open('txt/tags_refine.txt', 'r', encoding='utf-8') as fid:
                self.refine_tags = set([line.strip() for line in fid])

            stemmer = {}
            for f in string.ascii_lowercase:
                with open(os.path.join('txt/StemmingLexicon', f + '_s.txt')) as fid:
                    w_s = [line.strip() for line in fid]
                with open(os.path.join('txt/StemmingLexicon', f + '_d.txt')) as fid:
                    w_d = [line.strip() for line in fid]
                for i, w in enumerate(w_s):
                    stemmer[w] = w_d[i]
            self.stemmer = stemmer

            self.wnl = WordNetLemmatizer()

        elif stage == 5:
            with open('txt/filmetc.txt', 'r', encoding='utf-8') as fid:
                filmetc_li = [line.strip() for line in fid]
            self.filmetc_filter = ProfanitiesFilter(filmetc_li)

        elif stage == 6:
            with open('txt/boiler_plate.txt', 'r') as fid:
                boiler_plate = [line.strip() for line in fid]
            cw = []
            for sent in boiler_plate:
                words = sent.split(' ')
                cw.append((len(words), sent))
            cw = list(sorted(cw, reverse=True))
            boiler_plate = [c[1] for c in cw]
            self.boiler_plate = '|'.join(boiler_plate)

            # `boiler_regex_plate.txt` has been already sorted
            with open('txt/boiler_regex_plate.txt', 'r') as fid:
                regex_plate = [line.strip() for line in fid]
            self.boiler_regex_plate = '|'.join(regex_plate)

            # load predefined meaningless high freq sentences
            sents = set()
            with open('txt/blacksent.txt', 'r') as fid:
                for line in fid:
                    sents.add(line.strip().split('\t')[0])
            self.black_sents = sents

    def clean_sent(self, sent, pos_tags, stage):
        if stage == 4:
            return self.clean_sent_by_tag_refine(sent)
        elif stage == 5:
            return self.clean_sent_by_filmetc(sent)
        elif stage == 6:
            return self.clean_sent_by_meaningless(sent)
        else:
            raise NotImplementedError

    def clean_sent_by_tag_refine(self, sent):
        sent_set = [
            self.stemmer[word] 
            if word in self.stemmer 
            else word
            for word in sent.split()
        ]
        sent_set = [self.wnl.lemmatize(w) for w in sent_set]
        sent_set = [w for w in sent_set if w not in self.stop_words]
        sent_set = set(sent_set)
        if len(sent_set.intersection(self.refine_tags)) == 0:
            return 'none'

        return sent

    def clean_sent_by_filmetc(self, sent):
        if self.filmetc_filter.is_profanity(sent):
            return 'none'

        return sent
    
    def clean_sent_by_meaningless(self, sent):
        ## clip predefined meaningless web-related boiler plate
        sent = re.sub(self.boiler_plate, "", sent)
        sent = re.sub(self.boiler_regex_plate, "", sent)
        sent = self.unique_whitespace(sent)
        sent = sent.strip()
        words = sent.split(' ')
        if len(words) <= self.min_len:
            return 'none'

        ## discard predefined meaningless high freq sentences
        if sent in self.black_sents:
            return 'none'

        return sent