# Use this as our pornog-raphy/profanity detectors
# https://stackoverflow.com/questions/3531746/what-s-a-good-python-profanity-filter-library

import os
import re
import string
import unicodedata
import string
import nltk
from nltk.tokenize import word_tokenize
from config import cfg
import lib.utils as utils

from models.strong_profanities_filter import StrongProfanitiesFilter

def remove_punc(sent):
    tokens = sent.split()
    tokens = [w for w in tokens if not w in string.punctuation]
    new_sent = ' '.join(tokens)
    return new_sent

class BasicCleaner(object):
    def __init__(self, tokenizer=None):
        super(BasicCleaner, self).__init__()
        self.min_len = cfg.MIN_LEN
        self.max_len = cfg.MAX_LEN
        self.tokenizer = tokenizer

        self.load_blacklist()
        self.init_profanity_filter()
        
    def init_profanity_filter(self):
        self.pfilter = StrongProfanitiesFilter(self.blacklist)

    def load_blacklist(self):
        blacklist = utils.read_lines('txt/blacklist.txt')
        self.blacklist = set([x.strip().lower() for x in blacklist])
        blacklist_url = utils.read_lines('txt/blacklist_url.txt')
        self.blacklist_url = set([x.strip().lower() for x in blacklist_url])

    def clean_sent(self, sent):
        raise NotImplementedError

    # whether the url is ok
    def check_url(self, url):
        # can access
        pattern = r'^(http://|https://|//)'
        can_access = bool(re.match(pattern, url))
        if not can_access:
            return False
        # not in the blacklist
        for word in self.blacklist_url:
            if word in url:
                return False
        # not contain \n \r in url
        if not re.search(r"(\n|\r)", url) is None:
            return False
            
        return True

    def complete_url(self, url):
        if url.startswith('//'):
            url = 'https:' + url
        return url


class TokenizedBasicCleaner(BasicCleaner):
    PUNCTUATIONS = ["''", "'", "``", "`", "-LRB-", "-RRB-", "-LCB-", "-RCB-", \
        ".", "?", "!", ",", ":", "-", "--", "...", ";"] 

    def __init__(self, args, tokenizer=None):
        super(TokenizedBasicCleaner, self).__init__(tokenizer)
        self.args = args

        # predefined vocab refine dict:
        self.refined_vocab = {
            '&': 'and',
            ## abbreviation
            "\'d": 'would',
            "\'ll": 'will',
            "\'m": 'am',
            "\'re": 'are',
            "\'ve": 'have',
            "n\'t": 'not',
            'btw': 'by the way',

            # others
            'youre': 'you are',
            'youve': 'you have',
            'youll': 'you will',
            'weve': 'we have',
            'ive': 'i have',
            'thats': 'that is',
            'theres': 'there is',
            'theyre': 'they are',
            'wasnt': 'was not',
            'havent': 'have not',
            'couldnt': 'could not',
            'whos': 'who is',
            'arent': 'are not',
            'wouldnt': 'would not',
            'shouldnt': 'should not',
            'dont': 'do not',
            'doesnt': 'does not',
            'isnt': 'is not',
            'didnt': 'did not'
        }
        self.refined_vocab_keys = set(self.refined_vocab.keys())

    def clean_sent(self, sent):
        # trigger the pornog-raphy/profanity detectors
        if self.pfilter.is_profanity(sent):
            return 'none'

        tokens = nltk.word_tokenize(sent)
        tokens = [self.refined_vocab[w] if w in self.refined_vocab_keys else w for w in tokens]

        # classify "\'s" as POS or VBZ
        if "\'s" in tokens:
            tags = nltk.pos_tag(tokens)
            tokens = ['is' if x[0] == "\'s" and x[1] == 'VBZ' else x[0] for x in tags]

        sent = ' '.join([w for w in tokens if w not in self.PUNCTUATIONS])
        if self.args.remove_punc:
            # remove punc harder
            sent = remove_punc(sent)

        tokens = self.tokenizer.tokenize(sent)
        tokens = [w for w in tokens if w != '[UNK]']
        sent = self.tokenizer.convert_tokens_to_string(tokens)

        sent = "".join(ch if ch in string.printable else ' ' for ch in sent)
        total_len = len(sent.split())
        if total_len <= self.min_len or total_len > self.max_len:
            return 'none'

        return sent