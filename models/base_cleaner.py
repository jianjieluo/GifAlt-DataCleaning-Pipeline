import re
from config import cfg

class BaseCleaner(object):
    def __init__(self):
        super(BaseCleaner, self).__init__()
        self.min_len = cfg.MIN_LEN
        self.max_len = cfg.MAX_LEN

    def unique_whitespace(self, sent):
        return re.sub(' +', ' ', sent)