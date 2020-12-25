# predefined boiler-plate prefix/suffix
import os
import re
import nltk
from nltk.corpus import stopwords, words
from models.base_cleaner import BaseCleaner


class BoilerPlateCleaner(BaseCleaner):
    def __init__(self, boiler_plate_path='txt/boiler_plate2.txt'):
        super(BoilerPlateCleaner, self).__init__()
        # Load predefined boiler plate
        with open(boiler_plate_path, 'r') as fid:
            boiler_plate = [line.strip() for line in fid]
        cw = []
        for sent in boiler_plate:
            words = sent.split(' ')
            cw.append((len(words), sent))
        cw = list(sorted(cw, reverse=True))
        boiler_plate = [c[1] for c in cw]
        boiler_plate = [self.inword_pattern(b) for b in boiler_plate]

        self.boiler_plate = '|'.join(boiler_plate)
        self.head_tail_plate = r'(<bos>|<eos>)'

    def inword_pattern(self, pattern):
        if '<bos>' in pattern:
            return pattern + ' '
        elif '<eos>' in pattern:
            return ' ' + pattern
        else:
            raise NotImplementedError
        
    def add_head_tail(self, sent):
        return '<bos> %s <eos>' % sent
        
    def clean_sent(self, sent):
        sent = self.add_head_tail(sent)
        sent = re.sub(self.boiler_plate, "", sent)
        sent = re.sub(self.head_tail_plate, "", sent)
        sent = self.unique_whitespace(sent)
        sent = sent.strip()
        words = sent.split(' ')
        if len(words) <= self.min_len:
            return 'none'
        return sent


class RegexBoilerPlateCleaner(BoilerPlateCleaner):
    def __init__(self, boiler_plate_path=None, boiler_regex_plate_path=None):
        super(RegexBoilerPlateCleaner, self).__init__(boiler_plate_path)

        with open(boiler_regex_plate_path, 'r') as fid:
            regex_plate = [line.strip() for line in fid]
        self.boiler_regex_plate = '|'.join(regex_plate)

    def clean_sent(self, sent):
        sent = re.sub(self.boiler_regex_plate, "", sent)
        sent = self.unique_whitespace(sent)
        sent = sent.strip()
        sent = super(RegexBoilerPlateCleaner, self).clean_sent(sent)
        return sent